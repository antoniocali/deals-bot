import selectorlib
import requests
import re
import json
from typing import List, Optional
from app.models import DealsModel, Website
from slugify import slugify
from app.utils import removeSpecialFromPrice

headers = {
    "authority": "www.amazon.com",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "document",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
}


def _fetch_camel(params: dict = None) -> List[DealsModel]:
    r = requests.get("https://it.camelcamelcamel.com/top_drops", headers=headers)
    selector = selectorlib.Extractor.from_yaml_file(
        "./app/fetchers/selectors/camel_selector.yaml"
    )
    extracted = selector.extract(r.text)

    important_data = zip(
        extracted["discountPrice"],
        extracted["discountAmount"],
        extracted["description"],
        extracted["imageUrl"],
        extracted["link"],
    )
    print(extracted["link"])
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
        discount = 100 - int((discountPrice / (discountPrice + discountAmount)) * 100)
        dataAsinAndOriginalPrice.append(
            (
                discountPrice,
                "%.2f" % (discountPrice + discountAmount),
                discount,
                elem[2],
                elem[3],
                matcher.group(1),
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
                slug=slugify(item[3]),
            ),
            dataAsinAndOriginalPrice,
        )
    )


def _fetch_amazon(params: dict = None) -> List[DealsModel]:
    r = requests.get(
        f"https://www.amazon.it/gp/goldbox?gb_f_deals1={params['filter']}",
        headers=headers,
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


websites = {
    Website.CAMEL: _fetch_camel,
    Website.AMAZON: _fetch_amazon,
}


def fetch_data(website: Website, params: Optional[dict] = None) -> List[DealsModel]:
    return websites[website](params)

