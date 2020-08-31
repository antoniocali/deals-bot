from abc import ABC, abstractmethod
from urllib import parse
from app.models import DealsModel
import sys
from typing import List
import requests
import re
import json
import selectorlib
from slugify import slugify
from app.utils import Utils


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

        reg = r"\"dealDetails\"\s*:\s*{(.*?)}\s*\n\s*},"
        matcher = re.search(reg, r.text, flags=re.DOTALL)
        if not matcher:
            return []
        importantData = "{" + matcher.group(0)[:-2] + "} }"
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
        pageQuery = params["page"]
        discountQuery = params["min_discount"]
        maxPrice = params["max_price"]
        r = requests.get(
            f"https://it.camelcamelcamel.com/top_drops?p={pageQuery}",
            headers=self.headers,
        )
        selector = selectorlib.Extractor.from_yaml_file(
            "./app/fetchers/selectors/camel_selector.yaml"
        )
        extracted = selector.extract(r.text)
        if (
            not extracted["imageUrl"]
            or not extracted["discountPrice"]
            or not extracted["discountAmount"]
            or not extracted["link"]
        ):
            return list()
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
            # Look for the asin
            matcher = re.search(regex, elem[4])
            # If cannot retrieve the Asin
            if not matcher:
                # Skip the element
                continue

            # If the element is outofstock
            if elem[0].lower() == "out of stock":
                # skip the element
                continue

            discountPrice = float(Utils.removeSpecialFromPrice(elem[0]))
            # Check if discountPrice is higher than maxPrice
            if maxPrice and discountPrice > float(maxPrice):
                # In case it skips the element
                continue

            discountAmount = float(Utils.removeSpecialFromPrice(elem[1]))
            discount = 100 - int(
                (discountPrice / (discountPrice + discountAmount)) * 100
            )
            # Check if discount is lower than what we want
            if discountQuery and discount < discountQuery:
                # In case it skips the element
                continue

            description = elem[2]
            shortDescription = (
                description if len(description) < 30 else description[:30]
            )
            dataAsinAndOriginalPrice.append(
                (
                    round(discountPrice, 2),
                    round(discountPrice + discountAmount, 2),
                    discount,
                    elem[2],
                    elem[3],
                    matcher.group(1),
                    shortDescription,
                )
            )

        retList = list(
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
        )
        return retList


class InstantGamingFetcher(Fetcher):
    def __init__(self, headers: dict):
        self.headers = headers

    def fetch_data(self, params: dict) -> List[DealsModel]:
        url = "https://www.instant-gaming.com/it/ricerca/?instock=1&currency=EUR"
        r = requests.get(url, headers=self.headers,)
        return []


