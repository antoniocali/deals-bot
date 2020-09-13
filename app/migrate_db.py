from peewee import IntegerField
from playhouse.migrate import SqliteMigrator, migrate
from app.db import db
from app.db.tables import Deal, DealType, TelegramMessage
from app.models import TypeDeal

migrator = SqliteMigrator(db)

DealType.create_table()
Deal.create_table()


deal_field = IntegerField(null=False, default=TypeDeal.AMAZON.value)

for elem in TypeDeal:
    DealType.create(id=elem.value, description=elem.name)

migrate(
    migrator.rename_column("amazondeal", "asin", "id"),
    migrator.add_column("deal", "deal_type", deal_field),
    migrator.rename_table("deal", "amazondeal"),
    migrator.rename_table("telegrammessage", "telegrammessage_old")
)

TelegramMessage.create_table()

db.execute_sql(f"""
    INSERT INTO deal (id, deal_type_id, original_price, deal_price, percent_off, description, review_rating, image_url, updated_on, created_on)
    SELECT id, {TypeDeal.AMAZON.value}, original_price, deal_price, percent_off, description, review_rating, image_url, update_on, created_on
    FROM amazondeal
""")

db.execute_sql(f"""
    INSERT INTO telegrammessage (id, channel_id, deal_id, deal_type_id, sent_on, updated_on)
    SELECT id, channel_id, asin_id, {TypeDeal.AMAZON.value}, sent_on, updated_on
    FROM telegrammessage_old
""")


db.execute_sql("DROP TABLE AMAZONDEAL")
db.execute_sql("DROP TABLE telegrammessage_old")
