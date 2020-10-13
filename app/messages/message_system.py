from __future__ import annotations
from app.messages.model import Stats
from app.utils import Utils
from typing import Optional, List, Callable, Dict
from app.logger import getLogger
from app.models import DealsCategories, ShopsEnum, TypeDealsModel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_ALL,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_EXECUTED,
)
from datetime import datetime, date, timedelta
from app.config.config import Config
from app.db.database import Database
import requests

log = getLogger("MessageQueue")


class LockException(Exception):
    pass


class MessageQueue:
    __instance__ = None

    def __init__(self):
        """ Constructor.
       """
        if MessageQueue.__instance__ is None:
            MessageQueue.__instance__ = self
            self._scheduler = BackgroundScheduler()
            self._lock = False
            self._queue: List[TypeDealsModel] = list()
            triggers = CronTrigger.from_crontab("0 0 * * *")
            self._scheduler.add_listener(self._listener, mask=EVENT_ALL)
            self._scheduler.add_job(
                self._refresh,
                trigger=triggers,
                id="queue_system",
                next_run_time=datetime.now(),
            )
            self.first_run = True
            self.config = Config.get_instance()
            self.stats = Stats()
            self._scheduler.start()
            self.mappingShops: Dict[ShopsEnum, Callable[[], List[TypeDealsModel]]] = {
                ShopsEnum.INSTANT_GAMING : self._fetch_instant,
                ShopsEnum.AMAZON : self._fetch_camel
            }

    def _listener(self, event):
        if event.code == EVENT_JOB_ERROR:
            log.error("Refreshing Data Job Crashed :(")
        elif event.code == EVENT_JOB_ADDED:
            log.info("Refreshing Data Job Scheduled. Ready to be executed")
        elif event.code == EVENT_JOB_SUBMITTED:
            log.info("Refreshing Data Job Scheduled...")
        elif event.code == EVENT_JOB_EXECUTED:
            log.info(
                "Refreshing Data Job Scheduled. Next run at {next_run}".format(
                    next_run=self._scheduler.get_job("queue_system").next_run_time
                )
            )

    def isLock(self) -> bool:
        return self._lock or self.first_run

    def nextElem(self) -> Optional[TypeDealsModel]:
        if self._lock:
            raise LockException("Queue is locked")
        else:
            return self._queue.pop(0) if self._queue else None

    def _refresh(self) -> None:
        if not self._lock:
            self._lock = True
            self.stats = Stats()
            log.info("Refreshing Data")
            self._queue = self._get_deals_for_run()
            log.info("Data Refreshed")

            log.info(f"TOTAL DEALS: {self.stats.totalFind}")
            log.info(f"DEALS REMOVED BECAUSE ALREADY SENT: {self.stats.filter_out_db}")
            log.info(f"DEALS REMOVED BECAUSE SIMILAR: {self.stats.removed_similar}")
            log.info(f"FINAL QUEUE SIZE: {self.stats.queue}")
            log.info("Deals distributed as following")
            for elem in self.getQueueStats().items():
                log.info(
                    "{:<35}{:<40}".format(
                        elem[0] if elem[0] else "NO CATEGORY", elem[1]
                    )
                )
            if self.first_run:
                log.info("First Run Done!")
                self.first_run = False
            self._lock = False
        else:
            log.warning("Still refreshing data from previous run")

    def _get_deals_for_run(self) -> List[TypeDealsModel]:
        deals = []
        for shop in self.config.shops:
            deals.extend(self.mappingShops[shop]())
        deals = Utils.roundrobin(self.getQueueByCategories(deals))
        self.stats.queue = len(deals)
        return deals

    def _fetch_instant(self) -> List[TypeDealsModel]:
        log.info("INSTANT_GAMING - Start Fetching")
        url = "http://localhost:8000/instant"
        min_discount = self.config.deals_min_discount
        max_price = self.config.deals_max_price
        queryParams = "?"
        if min_discount:
            queryParams += f"min_discount={min_discount}"
        if max_price:
            queryParams += f"&max_price={max_price}"
        req = requests.get(url + queryParams)
        log.info("INSTANT_GAMING - NO MORE DATA TO FETCH")
        if req.ok:
            response = req.json()
            data = response
        else:
            return []
        deals = self.etl_deals(data)
        return deals

    def _fetch_camel(self) -> List[TypeDealsModel]:
        # Internal Fetch for camel
        def _fetch_more(
            page: int,
            min_discount: Optional[int] = None,
            max_price: Optional[int] = None,
            categories: Optional[List[DealsCategories]] = None,
        ) -> Optional[List[dict]]:
            """ Fetch as much deals as I can from Camel
            """
            url = "http://localhost:8000/"
            queryParams = f"?page={page}"
            if min_discount:
                queryParams += f"&min_discount={min_discount}"
            if max_price:
                queryParams += f"&max_price={max_price}"
            if categories:
                queryParams += (
                    f"&category={'&category='.join(map(lambda x: x.value, categories))}"
                )
            req = requests.get(url + f"camel{queryParams}")
            if req.ok:
                response = req.json()
                return response
            else:
                return None
        log.info("AMAZON - Start Fetching")
        # Params for fetching camel
        page = 1
        moreToFetch = True
        min_discount = self.config.deals_min_discount
        max_price = self.config.deals_max_price
        categories = (
            self.config.deals_categories
            if self.config.deals_filter_categories
            else None
        )
        data: List[dict] = list()
        while moreToFetch:
            _data = _fetch_more(
                page=page,
                min_discount=min_discount,
                max_price=max_price,
                categories=categories,
            )
            if not _data:
                log.info("AMAZON - No More Data to Fetch")
                moreToFetch = False
                continue
            data.extend(_data)
            page += 1
        deals: List[TypeDealsModel] = self.etl_deals(data)
        deals = self._remove_similar_products(deals)
        return deals

    def etl_deals(self, data: List[Dict]) -> List[TypeDealsModel]:
        database = Database()
        return list(
            filter(
                None,
                map(
                    self.filter_deals(
                        database=database,
                        channel_id=self.config.telegram_id,
                        config=self.config,
                    ),
                    data,
                ),
            )
        )

    def _remove_similar_products(
        self, deals: List[TypeDealsModel]
    ) -> List[TypeDealsModel]:
        tmpList: List[TypeDealsModel] = list()
        for deal in deals:
            if not any(
                map(
                    lambda x: False
                    if x == deal
                    else Utils.cosine_distance(
                        x.deal.description, deal.deal.description
                    )
                    > 0.85,
                    tmpList,
                )
            ):
                tmpList.append(deal)
            else:
                log.info("Found two similar products:")
                log.info(deal)
                self.stats.removed_similar += 1
                for x in tmpList:
                    if (
                        Utils.cosine_distance(x.deal.description, deal.deal.description)
                        > 0.85
                    ):
                        log.info(x)
                        break

        return tmpList

    def getQueueByCategories(
        self, queue: List[TypeDealsModel]
    ) -> Dict[Optional[DealsCategories], List[TypeDealsModel]]:
        categories: Dict[Optional[DealsCategories], List[TypeDealsModel]] = dict()
        for elem in queue:
            key = DealsCategories(elem.deal.category) if elem.deal.category else None
            if key in categories:
                categories[key].append(elem)
            else:
                categories[key] = [elem]
        return categories

    def getQueueStats(self) -> Dict[Optional[DealsCategories], int]:
        if self._lock and not self.first_run:
            return {}
        if not self._lock:
            self._lock = True
        stats: Dict[Optional[DealsCategories], int] = {
            x: len(y) for x, y in self.getQueueByCategories(self._queue).items()
        }
        if not self.first_run and self._lock:
            self._lock = False
        return stats

    def filter_deals(
        self, database: Database, channel_id: int, config: Config
    ) -> Callable[[dict], Optional[TypeDealsModel]]:
        """Filter valid deals. It looks if deal was already posted on telegram. It looks if it can be reposted in case.

        Parameters:
            :param: database
            :type: Database
            Database to connect

            :param: channel_id
            :type: int
            Telegram Channel id

        Returns:
            a function that accept a single dictionary and return a DealsModel

        """

        def filter_deal_wrapper(elem: dict) -> Optional[TypeDealsModel]:
            deal: TypeDealsModel = TypeDealsModel.parse_obj(elem)
            dbDeal = database.getDeal(deal=deal)
            self.stats.totalFind += 1
            if dbDeal and float(deal.deal.dealPrice) >= float(dbDeal.deal_price):
                searchTelegram = database.searchTelegramMessage(
                    channel_id=channel_id, deal=deal
                )
                if not searchTelegram:
                    return deal
                else:
                    last_sent: date = datetime.strptime(
                        searchTelegram.updated_on, "%Y-%m-%d %H:%M:%S%z"
                    ).date()
                    today = datetime.today().date()
                    timedifference: timedelta = today - last_sent
                    if timedifference.days >= config.telegram_repost_after_days:
                        return deal
                    else:
                        self.stats.filter_out_db += 1
                        return None
            else:
                return deal

        return filter_deal_wrapper

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
       """
        if not MessageQueue.__instance__:
            MessageQueue()

        return MessageQueue.__instance__
