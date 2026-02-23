from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import categories_col, items_col
from app.dependencies.auth import get_current_user
from app.schemas.category import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest
from app.services.categories import normalize_category_name
from app.services.serializers import category_response

router = APIRouter(prefix='/menu/categories', tags=['categories'])


@router.get('')
def get_categories(current_user=Depends(get_current_user)):
    cursor = categories_col.find({'restaurant_id': current_user['_id']}).sort([('name', 1)])
    return {'categories': [category_response(category).model_dump() for category in cursor]}


@router.post('', response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreateRequest, current_user=Depends(get_current_user)) -> CategoryResponse:
    normalized_name = normalize_category_name(payload.name)
    if not normalized_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category name cannot be empty')

    doc = {
        'restaurant_id': current_user['_id'],
        'name': normalized_name,
        'name_key': normalized_name.lower(),
        'description': payload.description.strip(),
        'image_url': payload.image_url.strip(),
        'created_at': datetime.now(timezone.utc),
    }
    try:
        inserted = categories_col.insert_one(doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category already exists') from exc

    created = categories_col.find_one({'_id': inserted.inserted_id})
    return category_response(created)


@router.put('/{category_id}', response_model=CategoryResponse)
def update_category(
    category_id: str, payload: CategoryUpdateRequest, current_user=Depends(get_current_user)
) -> CategoryResponse:
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid category id')

    current = categories_col.find_one({'_id': ObjectId(category_id), 'restaurant_id': current_user['_id']})
    if not current:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')

    normalized_name = normalize_category_name(payload.name)
    if not normalized_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category name cannot be empty')

    try:
        categories_col.update_one(
            {'_id': current['_id'], 'restaurant_id': current_user['_id']},
            {
                '$set': {
                    'name': normalized_name,
                    'name_key': normalized_name.lower(),
                    'description': payload.description.strip(),
                    'image_url': payload.image_url.strip(),
                    'updated_at': datetime.now(timezone.utc),
                }
            },
        )
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category already exists') from exc

    if current.get('name') != normalized_name:
        items_col.update_many(
            {'restaurant_id': current_user['_id'], 'category': current.get('name', '')},
            {'$set': {'category': normalized_name, 'updated_at': datetime.now(timezone.utc)}},
        )

    updated = categories_col.find_one({'_id': current['_id'], 'restaurant_id': current_user['_id']})
    return category_response(updated)


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, current_user=Depends(get_current_user)) -> None:
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid category id')

    current = categories_col.find_one({'_id': ObjectId(category_id), 'restaurant_id': current_user['_id']})
    if not current:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')

    items_col.delete_many({'restaurant_id': current_user['_id'], 'category': current.get('name', '')})
    categories_col.delete_one({'_id': current['_id'], 'restaurant_id': current_user['_id']})
