import requests
from app.config.config import Config
from typing import Callable, Optional, List, Dict
import math
import re
from collections import Counter
from datetime import datetime
from app.models import DealsModel, ShortenProvider, TypeDeal, TypeDealsModel


class Utils:
    @staticmethod
    def removeSpecialFromPrice(textInput: str) -> str:
        textInput = textInput.replace("€", "").replace("%", "")
        if "," in textInput:
            textInput = textInput.replace(".", "").replace(",", ".")
        return textInput

    @staticmethod
    def shortUrl(url: str, provider: ShortenProvider):
        short_url: Dict[ShortenProvider, Callable[[str], Optional[str]]] = {
            ShortenProvider.FREE: Utils._shortFree,
            ShortenProvider.SHORTEST: Utils._shortShortest,
            ShortenProvider.BITLY: Utils._shortBitly,
        }
        return short_url[provider](url)

    @staticmethod
    def _shortBitly(url: str) -> Optional[str]:
        config = Config.get_instance()
        provider = "https://api-ssl.bitly.com/v4/shorten"
        token = config.shorten_bitly_token
        headers = {"Authorization": f"Bearer {token}"}
        data = {"long_url": url}
        response = requests.post(provider, json=data, headers=headers)
        if response.ok:
            responseData = response.json()
            return responseData["link"]
        else:
            return None

    @staticmethod
    def _shortShortest(url: str) -> Optional[str]:
        config = Config.get_instance()
        provider = "https://api.shorte.st/v1/data/url"
        token = config.shorten_shortest_token
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
    def _shortFree(url: str) -> Optional[str]:
        provider = "https://goolnk.com/api/v1/shorten"
        data = {"url": url}
        response = requests.post(provider, data=data)
        if response.ok:
            responseData = response.json()
            return responseData["result_url"]
        else:
            return None

    @staticmethod
    def affiliateAmazon(deal: DealsModel) -> str:
        config = Config.get_instance()
        affiliateToken = config.amazon_affiliate
        asin = deal.id
        return f"https://www.amazon.it/gp/product/{asin}/ref=as_li_tl?creativeASIN={asin}&tag={affiliateToken}"

    @staticmethod
    def affiliateInstant(deal: DealsModel) -> str:
        config = Config.get_instance()
        affiliateToken = config.instant_gaming_affiliate
        return f"https://www.instant-gaming.com/it/{deal.id}-{deal.slug}/?igr={affiliateToken}"

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
    def message(deal: TypeDealsModel) -> str:
        config = Config.get_instance()
        message_template = config.telegram_message_template
        affialiateLink = Utils.generateUrl(deal)
        shortUrlProvider = config.shorten_provider
        shortUrl = Utils.shortUrl(url=affialiateLink, provider=shortUrlProvider)
        _deal = deal.deal
        # In case short Url doesn't work I use long url
        shortUrl = shortUrl if shortUrl else affialiateLink
        return message_template.format(
            originalPrice="%.2f" % _deal.originalPrice,
            dealPrice="%.2f" % _deal.dealPrice,
            discount=_deal.percentOff,
            url=shortUrl,
            description=_deal.description,
            hashtags=""
            if not _deal.category
            else f"#{' #'.join(Utils.generateHashtags(_deal.category))}",
        )

    @staticmethod
    def generateHashtags(
        text: str, min_letters: int = 3, delimitator: str = "-"
    ) -> List[str]:
        if not text:
            return []
        else:
            _split = text.strip().split(delimitator)
            return list(filter(lambda x: len(x) >= min_letters, _split))

    @staticmethod
    def generateUrl(deal: TypeDealsModel) -> str:
        generators: Dict[TypeDeal, Callable[[DealsModel], str]] = {
            TypeDeal.AMAZON: Utils.affiliateAmazon,
            TypeDeal.INSTANT_GAMING: Utils.affiliateInstant,
        }

        return generators[deal.dealType](deal.deal)

    @staticmethod
    def roundrobin(data: Dict) -> List:
        req = data.copy()
        index = 0
        final_list = list()
        while req:
            for key in list(req):
                try:
                    final_list.append(req[key][index])
                except IndexError:
                    del req[key]
            index += 1
        return final_list
