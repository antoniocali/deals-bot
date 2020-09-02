from __future__ import annotations
from app.utils import Utils
from typing import Optional, List, Callable
from app.logger import getLogger
from app.models import DealsModel
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
            self._queue: Optional[List[DealsModel]] = list()
            triggers = CronTrigger.from_crontab("0 0 * * *")
            self._scheduler.add_listener(self._listener, mask=EVENT_ALL)
            self._scheduler.add_job(
                self._refresh,
                trigger=triggers,
                id="queue_system",
                next_run_time=datetime.now(),
            )
            self._scheduler.start()

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
        return self._lock

    def nextElem(self) -> Optional[DealsModel]:
        if self._lock:
            raise LockException("Queue is locked")
        else:
            return self._queue.pop(0) if self._queue else None

    def _refresh(self) -> None:
        if not self._lock:
            self._lock = True
            log.info("Refreshing Data")
            self._queue = self._get_deals_for_run()
            log.info("Data Refreshed")
            self._lock = False
        else:
            log.warning("Still refreshing data from previous run")

    def _get_deals_for_run(self) -> Optional[List[DealsModel]]:
        database = Database()
        config = Config.get_instance()
        channel_id = config.telegram_id
        page = 1
        moreToFetch = True
        postPerDay = config.telegram_posts_per_day
        min_discount = config.deals_min_discount
        max_price = config.deals_max_price
        deals = list()
        while moreToFetch:
            data = self._fetch_more(
                page=page, min_discount=min_discount, max_price=max_price
            )
            if not data:
                log.info("No More Data to Fetch")
                moreToFetch = False
                continue
            valid_deals = filter(
                None,
                map(
                    self.filter_deals(
                        database=database, channel_id=channel_id, config=config
                    ),
                    data,
                ),
            )
            deals.extend(valid_deals)
            deals = self._remove_similar_products(deals)
            if len(deals) >= postPerDay:
                moreToFetch = False
                break
            page += 1
        return deals

    def _remove_similar_products(self, deals: List[DealsModel]) -> List[DealsModel]:
        tmpList: List[DealsModel] = list()
        for deal in deals:
            if not any(
                map(
                    lambda x: False
                    if x == deal
                    else Utils.cosine_distance(x.description, deal.description) > 0.85,
                    tmpList,
                )
            ):
                tmpList.append(deal)
            else:
                log.info("Found two similar products:")
                log.info(deal)
                for x in tmpList:
                    if Utils.cosine_distance(x.description, deal.description) > 0.85:
                        log.info(x)
                        break

        return tmpList

    def _fetch_more(
        self,
        page: int,
        min_discount: Optional[int] = None,
        max_price: Optional[int] = None,
    ) -> Optional[List[dict]]:
        """ Fetch as much deals as I can from Camel
        """
        url = "http://localhost:8000/"
        queryParams = f"?page={page}"
        if min_discount:
            queryParams += f"&min_discount={min_discount}"
        if max_price:
            queryParams += f"&max_price={max_price}"
        req = requests.get(url + f"camel{queryParams}")
        if req.ok:
            response = req.json()
            return response
        else:
            return None

    def filter_deals(
        self, database: Database, channel_id: int, config: Config
    ) -> Callable[[dict], Optional[DealsModel]]:
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

        def filter_deal_wrapper(elem: dict) -> Optional[DealsModel]:
            deal: DealsModel = DealsModel.parse_obj(elem)
            dbDeal = database.getDeal(deal.impressionAsin)
            if dbDeal and float(deal.dealPrice) >= float(dbDeal.deal_price):
                searchTelegram = database.searchTelegramMessage(
                    channel_id=channel_id, asin=deal.impressionAsin
                )
                if not searchTelegram:
                    return deal
                else:
                    log.info(
                        f"{dbDeal} already present in database. Check if can post anyway."
                    )
                    last_sent: date = datetime.strptime(
                        searchTelegram.updated_on, "%Y-%m-%d %H:%M:%S%z"
                    ).date()
                    today = datetime.today().date()
                    timedifference: timedelta = today - last_sent
                    if timedifference.days >= config.telegram_repost_after_days:
                        return deal
                    else:
                        log.info(
                            f"{dbDeal} - Cannot post - Days passed {timedifference.days} from last post",
                        )
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
