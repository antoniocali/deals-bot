from peewee import (
    SqliteDatabase,
    DoesNotExist,
)

from app.db.tables import AmazonDeal, TelegramMessage
from app.db import db
from datetime import datetime
from app.models import DealsModel, TelegramMessageModel
from typing import Optional, List

tables = [AmazonDeal, TelegramMessage]


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
        for table in tables:
            if not db.table_exists(table):
                self.db.create_tables([table])

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

    def _createTelegramMessage(
        self, telegramMsg: TelegramMessageModel, asin: str
    ) -> Optional[TelegramMessage]:
        deal: Optional[AmazonDeal] = self.getDeal(asin)
        if not deal:
            return None
        else:
            telegram = TelegramMessage.create(
                id=telegramMsg.id,
                channel_id=telegramMsg.channel_id,
                asin=deal,
                sent_on=telegramMsg.datetime,
            )
            return telegram

    def deals(self):
        deals = AmazonDeal.select()
        return deals
