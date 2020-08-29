from app.logger import getLogger
from datetime import datetime, timedelta, date
from app.db.database import Database
from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel, InputPeerUser
from telethon.errors import BotInvalidError
import requests
import time
from app.utils import (
    amazonAffiliateLink,
    shortenUrlAds,
    shortenUrlFree,
    delayBetweenTelegramMessages,
)
from app.utils.config import Config
from app.models import DealsModel, TelegramMessageModel
from typing import Optional, List, Callable
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers import cron
from apscheduler.events import (
    EVENT_ALL,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_ADDED,
)
from app.generators import image_util

url = "http://localhost:8000/"

config = Config.get_instance()
bot = TelegramClient("bot", config.api_id, config.api_hash).start(
    bot_token=config.bot_token
)

scheduler = BlockingScheduler()
log = getLogger("TELEBOT")


async def main():
    db = Database()
    channel: int = await get_channel()
    valid_deals = get_deals_for_run(database=db, channel_id=channel)
    if valid_deals:
        for deal in valid_deals:
            await send_message(
                deal=deal, database=db, channel=channel, save_on_db=True
            )
            next_run = datetime.now() + timedelta(
                minutes=delayBetweenTelegramMessages()
            )
            log.info(
                "Next post at {next_run}".format(
                    next_run=next_run.strftime("%Y/%m/%d %H:%M:%S")
                )
            )
            while datetime.now() <= next_run:
                time.sleep(60)

    else:
        # Send message to admin
        log.info(
            "I couldn't retrieve any new valid deals. I will sleep for a hour before trying again"
        )
        scheduler.pause_job("telegram")
        time.sleep(60 * 60)
        log.info("Resuming Job and see if new deals appeared.")
        scheduler.resume_job("telegram")


async def get_channel() -> int:
    channel_id = config.telegram_channel_id
    channel = await bot.get_input_entity(channel_id)
    if channel:
        if isinstance(channel, InputPeerUser):
            log.info(f"user id for {config.telegram_channel_id} : {channel.user_id}")
            return channel.user_id
        elif isinstance(channel, InputPeerChannel):
            log.info(
                f"channel id for {config.telegram_channel_id} : {channel.channel_id}"
            )
            return channel.channel_id
        else:
            raise BotInvalidError(f"{channel_id} is not a valid channel")
    else:
        raise BotInvalidError(f"{channel_id} is not a valid channel")


def get_deals_for_run(
    database: Database, channel_id: int
) -> Optional[List[DealsModel]]:
    page = 1
    moreToFetch = True
    postPerDay = config.telegram_posts_per_day
    deals = list()
    while moreToFetch:
        data = fetch_more(page)
        if not data:
            log.info("No More Data to Fetch")
            moreToFetch = False
            continue
        valid_deals = filter(
            None, map(filter_deals(database=database, channel_id=channel_id), data)
        )
        deals.extend(valid_deals)
        if len(deals) >= postPerDay:
            moreToFetch = False
            continue
        page += 1
    return deals


# Fetch as more deals as I can from Camel
def fetch_more(page: int) -> Optional[List[dict]]:
    """ Fetch as much deals as I can from Camel
    """
    req = requests.get(url + f"camel?page={page}")
    if req.ok:
        response = req.json()
        return response
    else:
        return None


def filter_deals(
    database: Database, channel_id: int
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


def message(
    originalPrice: float, dealPrice: float, discount: int, asin: str, description: str
) -> str:
    affialiateLink = amazonAffiliateLink(asin)
    shortUrlAds = config.short_use_ads
    shortUrl = (
        shortenUrlAds(amazonAffiliateLink(asin))
        if shortUrlAds
        else shortenUrlFree(amazonAffiliateLink(asin))
    )
    # In case short Url doesn't work I use long url
    shortUrl = shortUrl if shortUrl else affialiateLink
    return """
    ⚡ {description}
    💸💸💸 **Incredibile Offerta** 💸💸💸
    👎 Prezzo Originale: {originalPrice}€
    💰 Prezzo Scontato: {dealPrice}€
    Con **Sconto** del **{discount}%** 🤑🤑

    __URL Offerta__: {shortUrl}
    """.format(
        originalPrice="%.2f" % originalPrice,
        dealPrice="%.2f" % dealPrice,
        discount=discount,
        shortUrl=shortUrl,
        description=description,
    )


def start():
    log.info("Run Started")
    bot.loop.run_until_complete(main())


async def send_message(
    deal: DealsModel, database: Database, channel: int, save_on_db: bool = True
):
    path = image_util.create_image(
        originalPrice=deal.originalPrice,
        dealPrice=deal.dealPrice,
        imageUrl=deal.imageUrl,
        save_as=deal.impressionAsin,
    )
    if save_on_db:
        database.upsertDeal(deal)
    msg = await bot.send_file(
        channel,
        file=path,
        caption=message(
            deal.originalPrice,
            deal.dealPrice,
            deal.percentOff,
            deal.impressionAsin,
            deal.description,
        ),
        force_document=False,
    )
    if save_on_db:
        database.upsertTelegramMessage(
            TelegramMessageModel(id=msg.id, channel_id=channel, datetime=msg.date),
            deal.impressionAsin,
        )
    image_util.delete_tmp_image(path)


def listener_for_telegram(event):
    if event.code == EVENT_JOB_ERROR:
        print("The job crashed :(")
        scheduler.shutdown(wait=False)
    elif event.code == EVENT_JOB_ADDED:
        log.info("Job Added. Ready to be executed")
    elif event.code == EVENT_JOB_SUBMITTED:
        log.info("Job Starting...")
    elif event.code == EVENT_JOB_EXECUTED:
        log.info("Job Finished. Waiting for next run")


log.info("TELEBOT STARTED")
log.info("Adding event listener for issue")
scheduler.add_listener(listener_for_telegram, EVENT_ALL | EVENT_JOB_ERROR)
rangeTime = (f"{config.telegram_start_hour}" if config.telegram_start_hour else "") + (
    f"-{config.telegram_end_hour}" if config.telegram_end_hour else ""
)
log.info(f"Range Time of Working Hours: {rangeTime}")
triggers = cron.CronTrigger.from_crontab(f"*/5 {rangeTime} * * *")
log.info("Creating the Scheduler")
scheduler.add_job(
    start,
    trigger=triggers,
    max_instances=1,
    id="telegram",
    next_run_time=datetime.now(),
)
log.info("Scheduler Started")
scheduler.start()
