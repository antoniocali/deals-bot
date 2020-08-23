from telethon import TelegramClient
import requests
import yaml
import time

url = "http://localhost:8000/"


# Use a config file for moment
with open("./app/telegram/config.yaml", "r") as stream:
    config = yaml.safe_load(stream)
    api_id = config["api_id"]
    api_hash = config["api_hash"]
    bot_token = config["bot_token"]


bot = TelegramClient("bot", api_id, api_hash)
# Starting as a bot account


# But then we can use the client instance as usual
async def main():
    req = requests.get(url + "camel")
    if req.ok:
        response = req.json()
        for elem in response:
            channel = await bot.get_input_entity("t.me/provalolasd")
            print(channel)
            asin = elem["impressionAsin"]
            originalPrice = elem["originalPrice"]
            dealPrice = elem["dealPrice"]
            discount = elem["percentOff"]
            msg = await bot.send_message(
                channel, message=message(originalPrice, dealPrice, discount, asin),
            )
            time.sleep(5)
            print(msg)


def message(originalPrice: float, dealPrice: float, discount: int, asin: str) -> str:
    return f"""**Incredibile Offerta**
    **Asin**: {asin}
    **Prezzo Originale**: {originalPrice}€
    **Prezzo Scontato**: {dealPrice}€
    **Sconto**: {discount}% 
    """


with bot.start(bot_token=bot_token):
    bot.loop.run_until_complete(main())

