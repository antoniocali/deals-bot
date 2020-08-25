from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
)
from datetime import datetime
from os import path, makedirs

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


def info():
    db.connect()
    print(db.get_tables())
    db.close()
