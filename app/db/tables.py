from peewee import (
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    ForeignKeyField,
    Model,
    CompositeKey,
)
from datetime import datetime
from app.db import db


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


class TelegramMessage(BaseModel):
    id = IntegerField()
    channel_id = IntegerField()
    asin = ForeignKeyField(AmazonDeal)
    sent_on = DateTimeField(null=False)
    updated_on = DateTimeField(null=True, default=sent_on)
    primary_key = CompositeKey(id, channel_id, asin)

