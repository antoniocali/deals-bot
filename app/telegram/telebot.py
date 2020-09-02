from app.logger import getLogger
from datetime import datetime, timedelta
from app.db.database import Database
from telethon import TelegramClient
import time
from app.utils import Utils
from app.config.config import Config
from app.models import DealsModel, TelegramMessageModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers import interval
from apscheduler.events import (
    EVENT_ALL,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_ADDED,
)
from app.generators import image_util
from app.messages.message_system import MessageQueue


config = Config.get_instance()
bot = TelegramClient("bot", config.api_id, config.api_hash).start(
    bot_token=config.bot_token
)

scheduler = AsyncIOScheduler()
log = getLogger("TELEBOT")
messageQueue = MessageQueue.get_instance()


async def message_system():
    if not Utils.can_run():
        log.info("Cannot run because it's not between start_hour and end_hour")
        return
    db = Database()
    channel = config.telegram_id
    while messageQueue.isLock():
        time.sleep(10)
    valid_deal = messageQueue.nextElem()
    if valid_deal:
        await send_message(
            deal=valid_deal, database=db, channel=channel, save_on_db=True
        )
        next_run = datetime.now() + timedelta(
            minutes=Utils.delayBetweenTelegramMessages()
        )
        log.info(
            "Next post at {next_run}".format(
                next_run=next_run.strftime("%Y/%m/%d %H:%M:%S")
            )
        )
    else:
        # Send message to admin
        log.info(
            "I couldn't retrieve any new valid deals. I will sleep for a hour before trying again"
        )
        scheduler.pause_job("telegram")
        time.sleep(60 * 60)
        log.info("Resuming Job and see if new deals appeared.")
        scheduler.resume_job("telegram")


def message(
    originalPrice: float, dealPrice: float, discount: int, asin: str, description: str
) -> str:
    affialiateLink = Utils.amazonAffiliateLink(asin)
    shortUrlAds = config.short_use_ads
    shortUrl = (
        Utils.shortenUrlAds(affialiateLink)
        if shortUrlAds
        else Utils.shortenUrlFree(affialiateLink)
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


def start():
    log.info("TELEBOT STARTED")
    log.info("Adding event listener for issue")
    scheduler.add_listener(listener_for_telegram, EVENT_ALL | EVENT_JOB_ERROR)
    rangeTime = (
        f"{config.telegram_start_hour}" if config.telegram_start_hour else ""
    ) + (f"-{config.telegram_end_hour}" if config.telegram_end_hour else "")
    log.info(f"Range Time of Working Hours: {rangeTime}")
    triggers = interval.IntervalTrigger(minutes=Utils.delayBetweenTelegramMessages())
    log.info("Creating the Scheduler")
    scheduler.add_job(
        message_system,
        trigger=triggers,
        max_instances=1,
        id="telegram",
        next_run_time=datetime.now(),
    )
    log.info("Scheduler Started")
    scheduler.start()
    bot.loop.run_forever()


if __name__ == "__main__":
    log.info("**HELLO**")
    start()
