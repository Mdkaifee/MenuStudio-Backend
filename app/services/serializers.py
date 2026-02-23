from typing import Any, Dict

from app.schemas.category import CategoryResponse
from app.schemas.item import MenuItemResponse
from app.schemas.template import TemplateResponse


def parse_user(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'id': str(user_doc['_id']),
        'email': user_doc['email'],
        'restaurant_name': user_doc['restaurant_name'],
        'template_id': user_doc.get('template_id', 'classic-blue'),
    }


def menu_item_response(item_doc: Dict[str, Any]) -> MenuItemResponse:
    return MenuItemResponse(
        id=str(item_doc['_id']),
        restaurant_id=str(item_doc['restaurant_id']),
        name=item_doc['name'],
        category=item_doc['category'],
        description=item_doc.get('description', ''),
        image_url=item_doc.get('image_url', ''),
        price=float(item_doc['price']),
    )


def category_response(category_doc: Dict[str, Any]) -> CategoryResponse:
    return CategoryResponse(
        id=str(category_doc['_id']),
        restaurant_id=str(category_doc['restaurant_id']),
        name=category_doc['name'],
        description=category_doc.get('description', ''),
        image_url=category_doc.get('image_url', ''),
    )


def template_response(template_doc: Dict[str, Any]) -> TemplateResponse:
    return TemplateResponse(
        id=template_doc['id'],
        name=template_doc['name'],
        description=template_doc.get('description', ''),
        style_id=template_doc['style_id'],
        is_custom=template_doc['is_custom'],
        asset_url=template_doc.get('asset_url', ''),
        asset_type=template_doc.get('asset_type', ''),
    )
