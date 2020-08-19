from pydantic import BaseModel
from enum import IntEnum


class DealsModel(BaseModel):
    description: str
    impressionAsin: str
    imageUrl: str
    originalPrice: str
    dealPrice: str
    percentOff: int
    reviewRating: float


class DiscountRange(IntEnum):
    MIN = 0
    MEDIUM = 1
    HIGH = 2
    MAX = 3