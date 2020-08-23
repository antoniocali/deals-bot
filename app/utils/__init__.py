import requests
from app.utils.config import Config
from typing import Optional


def removeSpecialFromPrice(textInput: str) -> str:
    return textInput.replace(".", "").replace(",", ".").replace("€", "")


def shortenUrlAds(url: str) -> Optional[str]:
    provider = "https://api.shorte.st/v1/data/url"
    token = Config.get_instance().shortest_token
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
    affiliateToken = Config.get_instance().amazon_affiliate
    return f"https://www.amazon.it/gp/product/{asin}/ref=as_li_tl?creativeASIN={asin}&tag={affiliateToken}"


