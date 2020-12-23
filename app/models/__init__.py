from datetime import datetime
from pydantic import BaseModel
from enum import Enum, IntEnum
from dataclasses import dataclass
from typing import Dict, Optional


class DealsModel(BaseModel):
    description: str
    id: str
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


class DealsCategories(Enum):
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
    INSTANT = "instant-gaming-computer-videogames"


class ShopsEnum(IntEnum):
    AMAZON = 0
    INSTANT_GAMING = 1
    AMAZON_REAL = 2


mappingsShop: Dict[str, ShopsEnum] = {
    "amazon": ShopsEnum.AMAZON,
    "instant_gaming": ShopsEnum.INSTANT_GAMING,
    "amazon_real": ShopsEnum.AMAZON_REAL
}

mappingsCategories: Dict[str, DealsCategories] = {
    "other": DealsCategories.OTHER,
    "auto": DealsCategories.AUTO,
    "home": DealsCategories.HOME,
    "electronics": DealsCategories.ELECTRONICS,
    "computer": DealsCategories.COMPUTER,
    "film": DealsCategories.FILM,
    "toys": DealsCategories.TOYS,
    "lighting": DealsCategories.LIGHTING,
    "books": DealsCategories.BOOKS,
    "music": DealsCategories.MUSIC,
    "watches": DealsCategories.WATCHES,
    "shoes": DealsCategories.SHOES,
    "sport": DealsCategories.SPORT,
    "videogames": DealsCategories.VIDEOGAMES,
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
