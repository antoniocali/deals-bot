import requests
from app.utils.config import Config
from typing import Optional


def removeSpecialFromPrice(textInput: str) -> str:
    return textInput.replace(".", "").replace(",", ".").replace("€", "")


def shortenUrlAds(url: str) -> Optional[str]:
    config = Config.get_instance()
    provider = "https://api.shorte.st/v1/data/url"
    token = config.shortest_token
    headers = {"public-api-token": token}
    data = {"urlToShorten": url}
    response = requests.put(provider, data=data, headers=headers)
    if response.ok:
        responseData = response.json()
        if responseData["status"].lower() == "ok":
            return responseData["shortenedUrl"]
        else:
            return None
    else:
        return None


def shortenUrlFree(url: str) -> Optional[str]:
    provider = "https://goolnk.com/api/v1/shorten"
    data = {"url": url}
    response = requests.post(provider, data=data)
    if response.ok:
        responseData = response.json()
        return responseData["result_url"]
    else:
        return None


def amazonAffiliateLink(asin: str) -> str:
    config = Config.get_instance()
    affiliateToken = config.amazon_affiliate
    return f"https://www.amazon.it/gp/product/{asin}/ref=as_li_tl?creativeASIN={asin}&tag={affiliateToken}"


def delayBetweenTelegramMessages() -> int:
    config = Config.get_instance()
    if config.telegram_delay_message_minutes:
        return config.telegram_delay_message_minutes
    else:
        posts = config.telegram_posts_per_day
        start = config.telegram_start_hour
        stop = config.telegram_end_hour
        return int((stop - start) * 60 / posts)
