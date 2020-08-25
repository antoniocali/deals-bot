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


def create_tables():
    db.connect()
    if not db.table_exists(AmazonDeal):
        db.create_tables([AmazonDeal])
    db.close()


def getDeal(asin: str) -> Optional[AmazonDeal]:
    with db.connect():
        try:
            return AmazonDeal.get(AmazonDeal.asin == asin)
        except DoesNotExist:
            return None


def createDeal(deal: DealsModel) -> AmazonDeal:
    pass


def upsertDeal(deal: DealsModel, connected: bool = False):
    if not connected:
        db.connect()
    retDeal = getDeal(deal.impressionAsin)
    if not retDeal:
        createDeal(deal)
    elif deal.dealPrice < retDeal.deal_price:
        retDeal.deal_price = deal.dealPrice
        retDeal.update_on = datetime.now()
        retDeal.save()
    if not connected:
        db.close()


def upsertDeals(deals: List[DealsModel]):
    for deal in deals:
        upsertDeal(deal)

