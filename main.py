from fetch_data import fetch_data
from models import DealsModel, DiscountRange
from typing import List, Optional
from fastapi import FastAPI

app = FastAPI()


@app.get("/deals")
def get_deals(discount_range: Optional[DiscountRange] = None) -> List[DealsModel]:
    params = discountRangeQueryParam(discount_range) if discount_range else ""
    print(params)
    return fetch_data(params)


def discountRangeQueryParam(discountRange: DiscountRange) -> str:
    switcher = {0: "10-25%", 1: "25-50%", 2: "50-70%", 3: "70-"}
    return f"discountRanges:{switcher[discountRange]}"

