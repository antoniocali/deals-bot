from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from app.models import DealsCategories, DealsModel, TypeDeal, TypeDealsModel
from typing import List, Optional
from functools import reduce
import requests
import re
import json
import selectorlib
from slugify import slugify
from app.utils import Utils
import cfscrape
from time import sleep


class Fetcher(ABC):
    @abstractmethod
    def fetch_data(self, params: dict = None):
        pass


class FetcherAmazon(Fetcher):
    def __init__(self, headers: dict) -> None:
        self.headers = headers

    def fetch_data(self, params: dict) -> List[TypeDealsModel]:
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
                "id",
                "primaryImage",
                "maxBAmount",
                "maxDealPrice",
                "maxPercentOff",
                "reviewRating",
            ]
        )
        return list(
            map(
                lambda item: TypeDealsModel(
                    dealType=TypeDeal.AMAZON,
                    deal=DealsModel(
                        description=item["description"],
                        id=item["id"],
                        imageUrl=item["primaryImage"],
                        originalPrice=item["maxBAmount"],
                        dealPrice=item["maxDealPrice"],
                        percentOff=item["maxPercentOff"],
                        reviewRating=item["reviewRating"],
                        slug=slugify(item["description"]),
                    ),
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
        self.scraper = cfscrape.create_scraper()

    def fetch_data(self, params: dict = None) -> List[TypeDealsModel]:
        pageQuery: int = params["page"]
        minDiscount: int = params.get("min_discount", None)
        maxPrice: int = params.get("max_price", None)
        categories: List[DealsCategories] = params.get("categories", None)

        def flat_list(
            x: List[TypeDealsModel], y: List[TypeDealsModel]
        ) -> List[TypeDealsModel]:
            x.extend(y)
            return x

        if categories:
            tmpList: List[List[TypeDealsModel]] = list()
            for category in categories:
                tmpList.append(
                    self._get_data(
                        pageQuery=pageQuery,
                        maxPrice=maxPrice,
                        minDiscount=minDiscount,
                        category=category.value,
                    )
                )
                sleep(1 / 2)
            return reduce(flat_list, tmpList)
        else:
            return self._get_data(
                pageQuery=pageQuery, maxPrice=maxPrice, minDiscount=minDiscount
            )

    def _get_data(
        self,
        pageQuery: int,
        maxPrice: Optional[int] = None,
        minDiscount: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[TypeDealsModel]:
        url = "https://it.camelcamelcamel.com/top_drops"
        url += f"?p={pageQuery}"
        if category:
            url += f"&bn={category}"
        r = self.scraper.get(url, headers=self.headers,)
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
            if minDiscount and discount < minDiscount:
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
                lambda item: TypeDealsModel(
                    dealType=TypeDeal.AMAZON,
                    deal=DealsModel(
                        dealPrice=item[0],
                        originalPrice=item[1],
                        percentOff=item[2],
                        description=item[3],
                        imageUrl=item[4],
                        id=item[5],
                        slug=slugify(item[6]),
                        category=category,
                    ),
                ),
                dataAsinAndOriginalPrice,
            )
        )
        return retList


class FetcherInstantGaming(Fetcher):
    def __init__(self, headers: dict):
        self.headers = headers

    def fetch_data(self, params: dict) -> List[TypeDealsModel]:
        url = "https://www.instant-gaming.com/it/ricerca/?instock=1&currency=EUR"
        r = requests.get(url, headers=self.headers,)
        if not r.ok:
            return []

        selector = selectorlib.Extractor.from_yaml_file(
            "./app/fetchers/selectors/instant_gaming_selector.yaml"
        )
        extracted = selector.extract(r.text)
        importantData = zip(extracted["description"], extracted["html"])
        data: List[TypeDealsModel] = list()
        regex = r"it\/([0-9]+)-"
        for elem in importantData:
            description = elem[0]
            html = elem[1]
            soup = BeautifulSoup(html, "html.parser")
            link = soup.a["href"]
            imageUrl = soup.img["src"]
            matcher = re.search(regex, link)
            if not matcher:
                continue
            dealPrice = round(
                float(
                    Utils.removeSpecialFromPrice(
                        soup.find("div", {"class": "price"}).string.strip()
                    )
                ),
                2,
            )
            discount = abs(
                int(
                    Utils.removeSpecialFromPrice(
                        soup.find("div", {"class": "discount"}).string.strip()
                    )
                )
            )
            originalPrice = round(dealPrice + (dealPrice * discount) / 100, 2)
            data.append(
                TypeDealsModel(
                    dealType=TypeDeal.INSTANT_GAMING,
                    deal=DealsModel(
                        dealPrice=dealPrice,
                        originalPrice=originalPrice,
                        percentOff=discount,
                        description=description,
                        imageUrl=imageUrl,
                        id=matcher.group(1),
                        slug=slugify(description),
                        category=DealsCategories.INSTANT.value
                    ),
                )
            )
        return data
