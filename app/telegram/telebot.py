from app.logger import getLogger
from datetime import datetime, timedelta
from app.db.database import Database
from telethon import TelegramClient
from telethon.tl.tlobject import TLObject
import time
from app.utils import Utils
from app.config.config import Config
from app.models import DealsModel, TelegramMessageModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers import interval, date as datetrigger
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
    job = scheduler.get_job("telegram")
    if not job or not job.trigger:
        log.info(
            "Job not found - I assume last run delete the whole scheduling. Rescheduling."
        )
        triggers = interval.IntervalTrigger(
            minutes=Utils.delayBetweenTelegramMessages()
        )
        scheduler.add_job(
            message_system,
            trigger=triggers,
            max_instances=1,
            id="telegram",
            next_run_time=datetime.now(),
        )
    if not Utils.can_run():
        log.info("Cannot run because it's not between start_hour and end_hour")
        startHour = config.telegram_start_hour
        endHour = config.telegram_end_hour
        today = datetime.today()
        if startHour and startHour < endHour:
            scheduledTime = datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=startHour,
                minute=0,
                second=0,
            ) + timedelta(days=1)
            dateTrigger = datetrigger.DateTrigger(scheduledTime)
            job.reschedule(dateTrigger)
        elif endHour and endHour < startHour:
            scheduledTime = datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=endHour,
                minute=0,
                second=0,
            )
            dateTrigger = datetrigger.DateTrigger(scheduledTime)
            job.reschedule(dateTrigger)
        log.info(f"Rescheduling the job to {job.next_run_time}")
        return

    db = Database()
    channel_type = config.telegram_type_id
    channel_id = config.telegram_id
    while messageQueue.isLock():
        time.sleep(10)
    valid_deal = messageQueue.nextElem()
    if valid_deal:
        await send_message(
            deal=valid_deal,
            database=db,
            channel_type=channel_type,
            channel_id=channel_id,
            save_on_db=True,
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
            "I couldn't retrieve any new valid deals. Think about changing your filters"
        )


async def send_message(
    deal: DealsModel,
    database: Database,
    channel_type: TLObject,
    channel_id: int,
    save_on_db: bool = True,
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
        channel_type,
        file=path,
        caption=Utils.message(
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
            TelegramMessageModel(id=msg.id, channel_id=channel_id, datetime=msg.date),
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
