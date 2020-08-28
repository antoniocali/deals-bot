from os import path, makedirs
from peewee import SqliteDatabase

db_path = "./database/deals.db"

if not path.exists(path.abspath(path.dirname(db_path))):
    makedirs(path.abspath(path.dirname(db_path)))

db: SqliteDatabase = SqliteDatabase(db_path)
