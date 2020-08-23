from abc import ABC, abstractmethod
from app.models import DealsModel
from typing import List
import requests
import re
import json
import selectorlib
from slugify import slugify
from app.utils import removeSpecialFromPrice


class Fetcher(ABC):
    @abstractmethod
    def fetch_data(self, params: dict = None):
        pass


class FetcherAmazon(Fetcher):
    def __init__(self, headers: dict) -> None:
        self.headers = headers

    def fetch_data(self, params: dict) -> List[DealsModel]:
        r = requests.get(
            f"https://www.amazon.it/gp/goldbox?gb_f_deals1={params['filter']}",
            headers=self.headers,
        )

        reg = r"\"dealDetails\"\s*:\s*{(.*)}\n\s*},\n"
        matcher = re.search(reg, r.text, flags=re.DOTALL)
        if not matcher:
            return []
        importantData = "{" + matcher.group(0)[:-2] + "}"
        extracted = json.loads(importantData)
        mandatoryKeys = set(
            [
                "description",
                "impressionAsin",
                "primaryImage",
                "maxBAmount",
                "maxDealPrice",
                "maxPercentOff",
                "reviewRating",
            ]
        )
        return list(
            map(
                lambda item: DealsModel(
                    description=item["description"],
                    impressionAsin=item["impressionAsin"],
                    imageUrl=item["primaryImage"],
                    originalPrice=item["maxBAmount"],
                    dealPrice=item["maxDealPrice"],
                    percentOff=item["maxPercentOff"],
                    reviewRating=item["reviewRating"],
                    slug=slugify(item["description"]),
                ),
                filter(
                    lambda item: set(item.keys()).issuperset(mandatoryKeys),
                    extracted["dealDetails"].values(),
                ),
            )
        )


class FetcherCamel(Fetcher):
    def __init__(self, headers: dict) -> None:
        self.headers = headers

    def fetch_data(self, params: dict = None) -> List[DealsModel]:
        r = requests.get(
            "https://it.camelcamelcamel.com/top_drops", headers=self.headers
        )
        selector = selectorlib.Extractor.from_yaml_file(
            "./app/fetchers/selectors/camel_selector.yaml"
        )
        extracted = selector.extract(r.text)
        maxProduct = params["maxProduct"]
        important_data = zip(
            extracted["discountPrice"],
            extracted["discountAmount"],
            extracted["description"],
            extracted["imageUrl"],
            extracted["link"],
        )
        regex = r"product\/([A-Z0-9]{10})\?"
        dataAsinAndOriginalPrice = []
        for elem in important_data:
            matcher = re.search(regex, elem[4])
            if not matcher:
                continue
            if elem[0].lower() == "out of stock":
                continue
            discountPrice = float(removeSpecialFromPrice(elem[0]))
            discountAmount = float(removeSpecialFromPrice(elem[1]))
            discount = 100 - int(
                (discountPrice / (discountPrice + discountAmount)) * 100
            )
            description = elem[2]
            shortDescription = (
                description if len(description) < 30 else description[:30]
            )
            dataAsinAndOriginalPrice.append(
                (
                    discountPrice,
                    "%.2f" % (discountPrice + discountAmount),
                    discount,
                    elem[2],
                    elem[3],
                    matcher.group(1),
                    shortDescription,
                )
            )
        return list(
            map(
                lambda item: DealsModel(
                    dealPrice=item[0],
                    originalPrice=item[1],
                    percentOff=item[2],
                    description=item[3],
                    imageUrl=item[4],
                    impressionAsin=item[5],
                    slug=slugify(item[6]),
                ),
                dataAsinAndOriginalPrice,
            )
        )[:maxProduct]
