from datetime import datetime, timedelta, date
from app.db.database import Database
from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel
from telethon.errors import BotInvalidError
import requests
import schedule
import time
from app.utils import amazonAffiliateLink, shortenUrlAds, shortenUrlFree
from app.utils.config import Config
from app.models import DealsModel, TelegramMessageModel
from typing import Optional, List, Callable

url = "http://localhost:8000/"

config = Config.get_instance()
bot = TelegramClient("bot", config.api_id, config.api_hash).start(
    bot_token=config.bot_token
)


async def main():
    db = Database()
    channel: int = await get_channel()
    page = 0
    moreToFetch = True
    while moreToFetch:
        data = fetch_more(page)
        if not data:
            moreToFetch = False
            continue
        valid_deals = filter(None, map(filter_deals(db=db, channel_id=channel), data))
        for deal in valid_deals:
            db.upsertDeal(deal)
            msg = await bot.send_message(
                channel,
                message=message(
                    deal.originalPrice,
                    deal.dealPrice,
                    deal.percentOff,
                    deal.impressionAsin,
                ),
            )
            db.upsertTelegramMessage(
                TelegramMessageModel(id=msg.id, channel_id=channel, datetime=msg.date),
                deal.impressionAsin,
            )
            time.sleep(5)
        page = page + 1


async def get_channel() -> int:
    channel_id = config.telegram_channel_id
    channel = await bot.get_input_entity(channel_id)
    if channel and isinstance(channel, InputPeerChannel):
        return channel.channel_id
    else:
        raise BotInvalidError(f"{channel_id} is not a valid channel")


def fetch_more(page: int) -> Optional[List[dict]]:
    req = requests.get(url + "camel")
    # To fix. Just for testing
    if page > 3:
        return None
    if req.ok:
        response = req.json()
        return response
    else:
        return None


def filter_deals(
    db: Database, channel_id: int
) -> Callable[[dict], Optional[DealsModel]]:
    def filter_deal_wrapper(elem: dict) -> Optional[DealsModel]:
        deal: DealsModel = DealsModel.parse_obj(elem)
        dbDeal = db.getDeal(deal.impressionAsin)
        if dbDeal and float(deal.dealPrice) >= float(dbDeal.deal_price):
            searchTelegram = db.searchTelegramMessage(
                channel_id=channel_id, asin=deal.impressionAsin
            )
            if not searchTelegram:
                return deal
            else:
                last_sent: date = datetime.strptime(
                    searchTelegram.updated_on, "%Y-%m-%d %H:%M:%S%z"
                ).date()
                today = datetime.today().date()
                timedifference: timedelta = last_sent - today
                if timedifference.days >= config.telegram_repost_after_days:
                    return deal
                else:
                    print(dbDeal, "already present in database")
                    return None
        return deal

    return filter_deal_wrapper


def message(originalPrice: float, dealPrice: float, discount: int, asin: str) -> str:
    affialiateLink = amazonAffiliateLink(asin)
    shortUrlAds = config.short_use_ads
    shortUrl = (
        shortenUrlAds(amazonAffiliateLink(asin))
        if shortUrlAds
        else shortenUrlFree(amazonAffiliateLink(asin))
    )
    # In case short Url doesn't work I use long url
    shortUrl = shortUrl if shortUrl else affialiateLink
    return f"""**Incredibile Offerta**
    **Prezzo Originale**: {"%.2f" % originalPrice}€
    **Prezzo Scontato**: {"%.2f" % dealPrice}€
    **Sconto**: {discount}%

    __URL__: {shortUrl}
    """


def start():
    bot.loop.run_until_complete(main())


start()
# schedule.every(15).seconds.do(start)

# while 1:
#     schedule.run_pending()
#     time.sleep(30)
