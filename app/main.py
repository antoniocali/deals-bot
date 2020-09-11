from app.models import DealsModel, DiscountRange, TypeDealsModel, Website, AmazonDealsCategories
from typing import List, Optional
from fastapi import FastAPI, Query
from app.fetchers.fetcher import fetch_data

app = FastAPI()


@app.get("/amazon")
def get_deals_amazon(
    discount_range: Optional[DiscountRange] = None,
) -> List[TypeDealsModel]:
    params = discountRangeQueryParam(discount_range) if discount_range else ""
    return fetch_data(Website.AMAZON, {"filter": params})


@app.get("/camel")
def get_deals_camel(
    page: Optional[int] = 1,
    min_discount: Optional[int] = None,
    max_price: Optional[int] = None,
    category: Optional[List[AmazonDealsCategories]] = Query(None),
) -> List[TypeDealsModel]:
    return fetch_data(
        Website.CAMEL,
        {
            "page": page,
            "min_discount": min_discount,
            "max_price": max_price,
            "categories": category,
        },
    )


@app.get("/instant")
def get_deals_instant() -> List[TypeDealsModel]:
    return fetch_data(Website.INSTANT_GAMING, {})


def discountRangeQueryParam(discountRange: DiscountRange) -> str:
    switcher = {0: "10-25%", 1: "25-50%", 2: "50-70%", 3: "70-"}
    return f"discountRanges:{switcher[discountRange]}"
