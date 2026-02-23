import re

from bson import ObjectId
from fastapi import HTTPException, status

from app.core.database import categories_col


def normalize_category_name(name: str) -> str:
    return re.sub(r'\s+', ' ', name).strip()


def require_existing_category(restaurant_id: ObjectId, category_name: str) -> str:
    normalized_name = normalize_category_name(category_name)
    name_key = normalized_name.lower()
    existing = categories_col.find_one({'restaurant_id': restaurant_id, 'name_key': name_key})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Category not found. Please create category first.',
        )
    return existing['name']
