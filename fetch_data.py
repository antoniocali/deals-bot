# import generators.image_util
import requests
import re
import json
import pprint
from models import DealsModel
from typing import List

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


def fetch_data() -> List[DealsModel]:
    r = requests.get("https://www.amazon.it/gp/goldbox", headers=headers)

    reg = r"\"dealDetails\"\s*:\s*{(.*)}\n\s*},\n"
    m = re.search(reg, r.text, flags=re.DOTALL)
    importantData = "{" + m.group(0)[:-2] + "}"
    # lines = importantData.split("\n")
    extracted = json.loads(importantData)
    # items = extracted["dealDetails"].keys()
    pprint.pprint(extracted)
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
            ),
            extracted["dealDetails"].values(),
        )
    )
