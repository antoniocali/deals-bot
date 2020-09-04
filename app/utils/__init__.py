import requests
from app.config.config import Config
from typing import Optional
import math
import re
from collections import Counter
from datetime import datetime


class Utils:
    @staticmethod
    def removeSpecialFromPrice(textInput: str) -> str:
        return textInput.replace(".", "").replace(",", ".").replace("€", "")

    @staticmethod
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

    @staticmethod
    def shortenUrlFree(url: str) -> Optional[str]:
        provider = "https://goolnk.com/api/v1/shorten"
        data = {"url": url}
        response = requests.post(provider, data=data)
        if response.ok:
            responseData = response.json()
            return responseData["result_url"]
        else:
            return None

    @staticmethod
    def amazonAffiliateLink(asin: str) -> str:
        config = Config.get_instance()
        affiliateToken = config.amazon_affiliate
        return f"https://www.amazon.it/gp/product/{asin}/ref=as_li_tl?creativeASIN={asin}&tag={affiliateToken}"

    @staticmethod
    def delayBetweenTelegramMessages() -> int:
        config = Config.get_instance()
        if config.telegram_delay_message_minutes:
            return config.telegram_delay_message_minutes
        else:
            posts = config.telegram_posts_per_day
            start = config.telegram_start_hour
            stop = config.telegram_end_hour
            return int((stop - start) * 60 / posts)

    @staticmethod
    def cosine_distance(text_1: str, text_2: str) -> float:
        def text_to_vector(text: str) -> Counter:
            words = re.compile(r"\w+").findall(text)
            return Counter(words)

        vec_1 = text_to_vector(text_1)
        vec_2 = text_to_vector(text_2)
        intersection = set(vec_1.keys()) & set(vec_2.keys())
        numerator = sum([vec_1[x] * vec_2[x] for x in intersection])

        sum1 = sum([vec_1[x] ** 2 for x in list(vec_1.keys())])
        sum2 = sum([vec_2[x] ** 2 for x in list(vec_2.keys())])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    @staticmethod
    def can_run() -> bool:
        config = Config.get_instance()
        start_hour = config.telegram_start_hour
        end_hour = config.telegram_end_hour
        current_hour = datetime.now().hour
        if not end_hour:
            return True
        else:
            if end_hour < start_hour:
                return end_hour <= current_hour < 24 and 0 <= current_hour <= start_hour
            else:
                return start_hour <= current_hour <= end_hour

    @staticmethod
    def message(
        originalPrice: float,
        dealPrice: float,
        discount: int,
        asin: str,
        description: str,
    ) -> str:
        config = Config.get_instance()
        message_template = config.telegram_message_template
        affialiateLink = Utils.amazonAffiliateLink(asin)
        shortUrlAds = config.short_use_ads
        shortUrl = (
            Utils.shortenUrlAds(affialiateLink)
            if shortUrlAds
            else Utils.shortenUrlFree(affialiateLink)
        )
        # In case short Url doesn't work I use long url
        shortUrl = shortUrl if shortUrl else affialiateLink
        return message_template.format(
            originalPrice="%.2f" % originalPrice,
            dealPrice="%.2f" % dealPrice,
            discount=discount,
            url=shortUrl,
            description=description,
        )
