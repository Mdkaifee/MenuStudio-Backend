from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import items_col
from app.dependencies.auth import get_current_user
from app.schemas.item import MenuItemCreateRequest, MenuItemResponse, MenuItemUpdateRequest
from app.services.categories import require_existing_category
from app.services.serializers import menu_item_response

router = APIRouter(prefix='/menu/items', tags=['items'])


@router.post('', response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(payload: MenuItemCreateRequest, current_user=Depends(get_current_user)) -> MenuItemResponse:
    saved_category_name = require_existing_category(current_user['_id'], payload.category)
    item_doc = {
        'restaurant_id': current_user['_id'],
        'name': payload.name.strip(),
        'category': saved_category_name,
        'description': payload.description.strip(),
        'image_url': payload.image_url.strip(),
        'price': round(payload.price, 2),
        'created_at': datetime.now(timezone.utc),
    }
    inserted = items_col.insert_one(item_doc)
    saved = items_col.find_one({'_id': inserted.inserted_id})
    return menu_item_response(saved)


@router.put('/{item_id}', response_model=MenuItemResponse)
def update_menu_item(item_id: str, payload: MenuItemUpdateRequest, current_user=Depends(get_current_user)) -> MenuItemResponse:
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid item id')

    saved_category_name = require_existing_category(current_user['_id'], payload.category)

    result = items_col.update_one(
        {'_id': ObjectId(item_id), 'restaurant_id': current_user['_id']},
        {
            '$set': {
                'name': payload.name.strip(),
                'category': saved_category_name,
                'description': payload.description.strip(),
                'image_url': payload.image_url.strip(),
                'price': round(payload.price, 2),
                'updated_at': datetime.now(timezone.utc),
            }
        },
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')

    updated = items_col.find_one({'_id': ObjectId(item_id), 'restaurant_id': current_user['_id']})
    return menu_item_response(updated)


@router.get('')
def list_my_menu_items(current_user=Depends(get_current_user)):
    cursor = items_col.find({'restaurant_id': current_user['_id']}).sort([('category', 1), ('name', 1)])
    return {'items': [menu_item_response(item).model_dump() for item in cursor]}


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(item_id: str, current_user=Depends(get_current_user)) -> None:
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid item id')

    result = items_col.delete_one({'_id': ObjectId(item_id), 'restaurant_id': current_user['_id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
