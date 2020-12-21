from app.fetchers.models.fetching import FetcherAmazon
from app.fetchers.fetcher import headers

ig = FetcherAmazon(headers)
for elem in ig._get_deals({}):
    print(elem)

