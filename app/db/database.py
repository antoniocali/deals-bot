from peewee import (
    SqliteDatabase,
    DoesNotExist,
)

from app.db.tables import Deal, DealType, TelegramMessage
from app.db import db
from datetime import datetime
from app.models import TelegramMessageModel, TypeDealsModel
from typing import Optional

tables = [Deal, TelegramMessage, DealType]


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

    def getDeal(self, deal: TypeDealsModel) -> Optional[Deal]:
        try:
            _deal = Deal.get(
                Deal.id == deal.deal.id, Deal.deal_type == deal.dealType.value
            )
        except DoesNotExist:
            _deal = None
        finally:
            return _deal

    def _createDeal(self, deal: TypeDealsModel) -> Deal:
        d = deal.deal
        _deal = Deal.create(
            id=d.id,
            deal_type=deal.dealType.value,
            original_price=d.originalPrice,
            deal_price=d.dealPrice,
            percent_off=d.percentOff,
            description=d.description,
            review_rating=d.reviewRating,
            image_url=d.imageUrl,
        )
        return _deal

    def upsertDeal(self, deal: TypeDealsModel) -> Deal:
        retDeal = self.getDeal(deal)
        if not retDeal:
            return self._createDeal(deal)
        elif float(deal.deal.dealPrice) < retDeal.deal_price:
            retDeal.deal_price = deal.deal.dealPrice
            retDeal.update_on = datetime.now()
            retDeal.save()
        return retDeal

    def _createTelegramMessage(
        self, telegramMsg: TelegramMessageModel, deal: TypeDealsModel
    ) -> Optional[TelegramMessage]:
        _deal: Optional[Deal] = self.getDeal(deal)
        if not _deal:
            return None
        else:
            telegram = TelegramMessage.create(
                id=telegramMsg.id,
                channel_id=telegramMsg.channel_id,
                deal=_deal,
                deal_type=deal.dealType.value,
                sent_on=telegramMsg.datetime,
                updated_on=telegramMsg.datetime,
            )
            return telegram

    def getTelegramMessage(
        self, telegramMsg: TelegramMessageModel, deal: TypeDealsModel
    ) -> Optional[TelegramMessage]:
        try:
            _deal = self.getDeal(deal)
            telMsg = TelegramMessage.get(
                TelegramMessage.id == telegramMsg.id,
                TelegramMessage.channel_id == telegramMsg.channel_id,
                TelegramMessage.deal == _deal,
                TelegramMessage.deal_type == deal.dealType.value,
            )
        except DoesNotExist:
            telMsg = None
        finally:
            return telMsg

    def upsertTelegramMessage(
        self, telegramMsg: TelegramMessageModel, deal: TypeDealsModel
    ) -> Optional[TelegramMessage]:
        retTelegram = self.searchTelegramMessage(channel_id=telegramMsg.channel_id, deal=deal)
        if not retTelegram:
            return self._createTelegramMessage(telegramMsg=telegramMsg, deal=deal)
        else:
            retTelegram.updated_on = telegramMsg.datetime
            retTelegram.save()
        return retTelegram

    def searchTelegramMessage(
        self, channel_id: int, deal: TypeDealsModel
    ) -> Optional[TelegramMessage]:
        try:
            _deal = self.getDeal(deal=deal)
            telMsg = TelegramMessage.get(
                TelegramMessage.channel_id == channel_id,
                TelegramMessage.deal == _deal,
                TelegramMessage.deal_type == deal.dealType.value,
            )
        except DoesNotExist:
            telMsg = None
        finally:
            return telMsg

    def deals(self):
        deals = Deal.select()
        return deals
