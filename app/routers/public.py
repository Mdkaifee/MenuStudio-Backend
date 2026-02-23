from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from app.core.database import categories_col, items_col, users_col
from app.services.serializers import menu_item_response
from app.services.templates import builtin_templates, find_template_for_restaurant

router = APIRouter(prefix='/public', tags=['public'])


@router.get('/menu/{restaurant_id}')
def public_menu(restaurant_id: str) -> Dict[str, Any]:
    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Restaurant not found')

    restaurant = users_col.find_one({'_id': ObjectId(restaurant_id)})
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Restaurant not found')

    selected_template_id = restaurant.get('template_id', 'classic-blue')
    selected_template = find_template_for_restaurant(restaurant['_id'], selected_template_id)
    if not selected_template:
        selected_template = builtin_templates()[0]

    categories_cursor = categories_col.find({'restaurant_id': restaurant['_id']})
    category_meta: Dict[str, Dict[str, str]] = {}
    for category_doc in categories_cursor:
        category_meta[category_doc['name']] = {
            'description': category_doc.get('description', ''),
            'image_url': category_doc.get('image_url', ''),
        }

    items_cursor = items_col.find({'restaurant_id': restaurant['_id']}).sort([('category', 1), ('name', 1)])
    items = [menu_item_response(item).model_dump() for item in items_cursor]

    categories: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        categories.setdefault(item['category'], []).append(item)

    return {
        'restaurant_id': str(restaurant['_id']),
        'restaurant_name': restaurant['restaurant_name'],
        'template_id': selected_template['id'],
        'template_style_id': selected_template['style_id'],
        'template_asset_url': selected_template.get('asset_url', ''),
        'template_asset_type': selected_template.get('asset_type', ''),
        'category_meta': category_meta,
        'categories': categories,
    }
