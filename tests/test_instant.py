from app.fetchers.models.fetching import FetcherInstantGaming
from app.fetchers.fetcher import headers

ig = FetcherInstantGaming(headers)
for elem in ig.fetch_data({}):
    print(elem)


