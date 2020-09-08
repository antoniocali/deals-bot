from app.fetchers.models.fetching import FetcherCamel
from app.fetchers.fetcher import headers

ig = FetcherCamel(headers)
for elem in ig.fetch_data({"categories": ["elettronica", "film-e-tv"], "page": 1}):
    print(elem)

