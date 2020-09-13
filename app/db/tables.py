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


class DealType(BaseModel):
    id = IntegerField(primary_key=True)
    description = CharField(null=False)


class Deal(BaseModel):
    id = CharField()
    deal_type = ForeignKeyField(DealType)
    original_price = FloatField(null=False)
    deal_price = FloatField(null=False)
    percent_off = IntegerField(null=False)
    description = CharField(null=True)
    review_rating = FloatField(null=False)
    image_url = CharField(null=True)
    updated_on = DateTimeField(null=True)
    created_on = DateTimeField(null=False, default=datetime.now())
    primary_key = CompositeKey(id, deal_type)


class TelegramMessage(BaseModel):
    id = IntegerField()
    channel_id = IntegerField()
    deal = ForeignKeyField(Deal)
    deal_type = ForeignKeyField(DealType)
    sent_on = DateTimeField(null=False)
    updated_on = DateTimeField(null=True, default=sent_on)
    primary_key = CompositeKey(id, channel_id, deal, deal_type)
