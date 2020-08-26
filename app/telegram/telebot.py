from app.db.database import AmazonDeal, Database
from telethon import TelegramClient
import requests
import time
import schedule
from app.utils import amazonAffiliateLink, shortenUrlAds, shortenUrlFree
from app.utils.config import Config
from app.db import database
from app.models import DealsModel

url = "http://localhost:8000/"

config = Config.get_instance()
bot = TelegramClient("bot", config.api_id, config.api_hash).start(
    bot_token=config.bot_token
)
# Starting as a bot account


# But then we can use the client instance as usual
async def main():
    req = requests.get(url + "camel?maxProduct=2")
    db = Database()
    if req.ok:
        response = req.json()
        for elem in response:
            deal: DealsModel = DealsModel.parse_obj(elem)
            dbDeal = db.getDeal(deal.impressionAsin)
            if dbDeal and float(deal.dealPrice) >= float(dbDeal.deal_price):
                print(dbDeal, "already present in database")
                continue
            db.upsertDeal(deal)
            # channel = await bot.get_input_entity("t.me/provalolasd")
            # msg = await bot.send_message(
            #     channel,
            #     message=message(
            #         deal.originalPrice,
            #         deal.dealPrice,
            #         deal.percentOff,
            #         deal.impressionAsin,
            #     ),
            # )
            time.sleep(5)


def message(originalPrice: str, dealPrice: str, discount: int, asin: str) -> str:
    affialeLink = amazonAffiliateLink(asin)
    shortUrlAds = config.short_url_ads
    shortUrl = (
        shortenUrlAds(amazonAffiliateLink(asin))
        if shortUrlAds
        else shortenUrlFree(amazonAffiliateLink(asin))
    )
    shortUrl = shortUrl if shortUrl else affialeLink
    return f"""**Incredibile Offerta**
    **Prezzo Originale**: {originalPrice}€
    **Prezzo Scontato**: {dealPrice}€
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
