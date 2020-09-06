from datetime import datetime
from pydantic import BaseModel
from enum import IntEnum
from dataclasses import dataclass


class DealsModel(BaseModel):
    description: str
    impressionAsin: str
    imageUrl: str
    originalPrice: float
    dealPrice: float
    percentOff: int
    slug: str
    reviewRating: float = -1


class DiscountRange(IntEnum):
    MIN = 0
    MEDIUM = 1
    HIGH = 2
    MAX = 3


class Website(IntEnum):
    CAMEL = 0
    AMAZON = 1
    INSTANT_GAMING = 2


class ShortenProvider(IntEnum):
    FREE = 0
    BITLY = 1
    SHORTEST = 2


@dataclass
class TelegramMessageModel:
    id: int
    channel_id: int
    datetime: datetime
