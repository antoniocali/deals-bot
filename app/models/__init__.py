from datetime import datetime
from pydantic import BaseModel
from enum import Enum, IntEnum
from dataclasses import dataclass
from typing import Dict, Optional


class DealsModel(BaseModel):
    description: str
    impressionAsin: str
    imageUrl: str
    originalPrice: float
    dealPrice: float
    percentOff: int
    slug: str
    category: Optional[str] = None
    reviewRating: float = -1


class TypeDeal(IntEnum):
    AMAZON = 0
    INSTANT_GAMING = 1


class TypeDealsModel(BaseModel):
    dealType: TypeDeal
    deal: DealsModel


class DiscountRange(IntEnum):
    MIN = 0
    MEDIUM = 1
    HIGH = 2
    MAX = 3


class Website(IntEnum):
    CAMEL = 0
    AMAZON = 1
    INSTANT_GAMING = 2


class AmazonDealsCategories(Enum):
    OTHER = "altro"
    AUTO = "auto-e-moto"
    HOME = "casa-e-cucina"
    # Smartphones, Headphones, Covers, TVs..
    ELECTRONICS = "elettronica"
    COMPUTER = "informatica"
    FILM = "film-e-tv"
    TOYS = "giochi-e-giocattoli"
    LIGHTING = "illuminazione"
    BOOKS = "libri"
    MUSIC = "musica"
    WATCHES = "orologi"
    SHOES = "scarpe-e-borse"
    SPORT = "sport-e-tempo-libero"
    VIDEOGAMES = "videogiochi"


mappingsCategories: Dict[str, AmazonDealsCategories] = {
    "other": AmazonDealsCategories.OTHER,
    "auto": AmazonDealsCategories.AUTO,
    "home": AmazonDealsCategories.HOME,
    "electronics": AmazonDealsCategories.ELECTRONICS,
    "computer": AmazonDealsCategories.COMPUTER,
    "film": AmazonDealsCategories.FILM,
    "toys": AmazonDealsCategories.TOYS,
    "lighting": AmazonDealsCategories.LIGHTING,
    "books": AmazonDealsCategories.BOOKS,
    "music": AmazonDealsCategories.MUSIC,
    "watches": AmazonDealsCategories.WATCHES,
    "shoes": AmazonDealsCategories.SHOES,
    "sport": AmazonDealsCategories.SPORT,
    "videogames": AmazonDealsCategories.VIDEOGAMES,
}


class ShortenProvider(IntEnum):
    FREE = 0
    BITLY = 1
    SHORTEST = 2


@dataclass
class TelegramMessageModel:
    id: int
    channel_id: int
    datetime: datetime
