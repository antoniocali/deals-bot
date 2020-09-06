from typing import List, Optional
from app.models import DealsModel, Website
from app.fetchers.models.fetching import FetcherAmazon, FetcherCamel, FetcherInstantGaming


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


websites = {
    Website.CAMEL: FetcherCamel(headers=headers),
    Website.AMAZON: FetcherAmazon(headers=headers),
    Website.INSTANT_GAMING: FetcherInstantGaming(headers=headers)
}


def fetch_data(website: Website, params: Optional[dict] = None) -> List[DealsModel]:
    return websites[website].fetch_data(params)
