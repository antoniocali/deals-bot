from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    DoesNotExist,
)
from datetime import datetime
from os import path, makedirs
from app.models import DealsModel
from typing import Optional, List

db_path = "./database/deals.db"

if not path.exists(path.abspath(path.dirname(db_path))):
    makedirs(path.abspath(path.dirname(db_path)))

db = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = db


class AmazonDeal(BaseModel):
    asin = CharField(primary_key=True)
    original_price = FloatField(null=False)
    deal_price = FloatField(null=False)
    percent_off = IntegerField(null=False)
    description = CharField(null=True)
    review_rating = FloatField(null=False)
    image_url = CharField(null=True)
    update_on = DateTimeField(null=True)
    created_on = DateTimeField(null=False, default=datetime.now())


class Database:
    def __init__(self) -> None:
        self.db: SqliteDatabase = db

    def connect(self):
        if self.db.is_closed:
            self.db.connect()

    def close(self):
        if not self.db.is_closed:
            self.db.close()

    def create_tables(self):
        self.db.connect()
        if not db.table_exists(AmazonDeal):
            self.db.create_tables([AmazonDeal])
        self.db.close()

    def getDeal(self, asin: str) -> Optional[AmazonDeal]:
        try:
            deal = AmazonDeal.get(AmazonDeal.asin == asin)
        except DoesNotExist:
            deal = None
        return deal

    def _createDeal(self, deal: DealsModel) -> AmazonDeal:
        deal = AmazonDeal.create(
            asin=deal.impressionAsin,
            original_price=deal.originalPrice,
            deal_price=deal.dealPrice,
            percent_off=deal.percentOff,
            description=deal.description,
            review_rating=deal.reviewRating,
            image_url=deal.imageUrl,
        )
        return deal

    def upsertDeal(self, deal: DealsModel):
        retDeal = self.getDeal(deal.impressionAsin)
        if not retDeal:
            self._createDeal(deal)
        elif float(deal.dealPrice) < float(retDeal.deal_price):
            retDeal.deal_price = deal.dealPrice
            retDeal.update_on = datetime.now()
            retDeal.save()

    def upsertDeals(self, deals: List[DealsModel]):
        for deal in deals:
            self.upsertDeal(deal)

    def deals(self):
        deals = AmazonDeal.select()
        return deals
