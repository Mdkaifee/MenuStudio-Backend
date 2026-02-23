from pymongo import ASCENDING, MongoClient

from app.core.config import MONGO_URI

client = MongoClient(MONGO_URI)
default_db = client.get_default_database()
db = default_db if default_db is not None else client['MenuApp']

users_col = db['users']
items_col = db['menu_items']
categories_col = db['menu_categories']
templates_col = db['menu_templates']


def init_indexes() -> None:
    users_col.create_index([('email', ASCENDING)], unique=True)
    items_col.create_index([('restaurant_id', ASCENDING), ('category', ASCENDING)])
    categories_col.create_index([('restaurant_id', ASCENDING), ('name_key', ASCENDING)], unique=True)
    templates_col.create_index([('restaurant_id', ASCENDING), ('name_key', ASCENDING)], unique=True)


def cleanup_legacy_template_columns() -> None:
    templates_col.update_many({'base_template_id': {'$exists': True}}, {'$unset': {'base_template_id': ''}})


init_indexes()
cleanup_legacy_template_columns()
