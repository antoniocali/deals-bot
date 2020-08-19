from pydantic import BaseModel


class DealsModel(BaseModel):
    description: str
    impressionAsin: str
    imageUrl: str
    originalPrice: str
    dealPrice: str
    percentOff: int
    reviewRating: float
