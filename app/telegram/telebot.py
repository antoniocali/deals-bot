from telethon import TelegramClient
import requests
import time
from app.utils import amazonAffiliateLink, shortenUrlAds, shortenUrlFree
from app.utils.config import Config

url = "http://localhost:8000/"

config = Config.get_instance()
bot = TelegramClient("bot", config.api_id, config.api_hash)
# Starting as a bot account


# But then we can use the client instance as usual
async def main():
    req = requests.get(url + "camel?maxProduct=1")
    if req.ok:
        response = req.json()
        for elem in response:
            channel = await bot.get_input_entity("t.me/provalolasd")
            asin = elem["impressionAsin"]
            originalPrice = elem["originalPrice"]
            dealPrice = elem["dealPrice"]
            discount = elem["percentOff"]
            msg = await bot.send_message(
                channel, message=message(originalPrice, dealPrice, discount, asin),
            )
            print(msg)
            time.sleep(5)


def message(originalPrice: float, dealPrice: float, discount: int, asin: str) -> str:
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


with bot.start(bot_token=config.bot_token):
    bot.loop.run_until_complete(main())

