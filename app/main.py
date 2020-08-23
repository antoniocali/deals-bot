from app.models import DealsModel, DiscountRange, Website
from typing import List, Optional
from fastapi import FastAPI
from app.fetchers.fetcher import fetch_data

app = FastAPI()


@app.get("/amazon")
def get_deals_amazon(discount_range: Optional[DiscountRange] = None) -> List[DealsModel]:
    params = discountRangeQueryParam(discount_range) if discount_range else ""
    return fetch_data(Website.AMAZON, {"filter": params})


@app.get("/camel")
def get_deals_camel() -> List[DealsModel]:
    return fetch_data(Website.CAMEL)


def discountRangeQueryParam(discountRange: DiscountRange) -> str:
    switcher = {0: "10-25%", 1: "25-50%", 2: "50-70%", 3: "70-"}
    return f"discountRanges:{switcher[discountRange]}"

