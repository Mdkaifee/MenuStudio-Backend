from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import templates_col, users_col
from app.dependencies.auth import get_current_user
from app.schemas.template import TemplateCreateRequest, TemplateResponse, TemplateSelectionRequest, TemplateUpdateRequest
from app.services.serializers import parse_user, template_response
from app.services.templates import (
    all_templates_for_restaurant,
    builtin_templates,
    find_template_for_restaurant,
    normalize_template_name,
)

router = APIRouter(tags=['templates'])


def _resolve_template_asset_fields(asset_url_raw: str, asset_type_raw: str):
    asset_url = asset_url_raw.strip()
    asset_type = asset_type_raw.strip().lower()

    if not asset_url and not asset_type:
        return '', ''

    if asset_url and not asset_type:
        if asset_url.startswith('data:image/'):
            asset_type = 'image'
        elif asset_url.startswith('data:application/pdf'):
            asset_type = 'pdf'
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid template file type')

    if asset_type and not asset_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Template file is required for file type')

    if asset_type not in {'image', 'pdf'}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid template file type')

    return asset_url, asset_type


@router.get('/templates')
def get_templates(current_user=Depends(get_current_user)):
    return {'templates': builtin_templates()}


@router.get('/restaurant/templates')
def get_restaurant_templates(current_user=Depends(get_current_user)):
    templates = all_templates_for_restaurant(current_user['_id'])
    return {'templates': [template_response(tpl).model_dump() for tpl in templates]}


@router.post('/restaurant/templates', response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant_template(payload: TemplateCreateRequest, current_user=Depends(get_current_user)) -> TemplateResponse:
    template_name = normalize_template_name(payload.name)
    if not template_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Template name cannot be empty')

    asset_url, asset_type = _resolve_template_asset_fields(payload.asset_url, payload.asset_type)

    doc = {
        'restaurant_id': current_user['_id'],
        'name': template_name,
        'name_key': template_name.lower(),
        'description': payload.description.strip(),
        'asset_url': asset_url,
        'asset_type': asset_type,
        'created_at': datetime.now(timezone.utc),
    }

    try:
        inserted = templates_col.insert_one(doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Template already exists') from exc

    created = templates_col.find_one({'_id': inserted.inserted_id})
    return template_response(
        {
            'id': str(created['_id']),
            'name': created['name'],
            'description': created.get('description', ''),
            'style_id': 'classic-blue',
            'is_custom': True,
            'asset_url': created.get('asset_url', ''),
            'asset_type': created.get('asset_type', ''),
        }
    )


@router.put('/restaurant/templates/{template_id}', response_model=TemplateResponse)
def update_restaurant_template(
    template_id: str, payload: TemplateUpdateRequest, current_user=Depends(get_current_user)
) -> TemplateResponse:
    if not ObjectId.is_valid(template_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid template id')

    template_name = normalize_template_name(payload.name)
    if not template_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Template name cannot be empty')

    asset_url, asset_type = _resolve_template_asset_fields(payload.asset_url, payload.asset_type)

    try:
        result = templates_col.update_one(
            {'_id': ObjectId(template_id), 'restaurant_id': current_user['_id']},
            {
                '$set': {
                    'name': template_name,
                    'name_key': template_name.lower(),
                    'description': payload.description.strip(),
                    'asset_url': asset_url,
                    'asset_type': asset_type,
                    'updated_at': datetime.now(timezone.utc),
                }
            },
        )
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Template already exists') from exc

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')

    updated = templates_col.find_one({'_id': ObjectId(template_id), 'restaurant_id': current_user['_id']})
    return template_response(
        {
            'id': str(updated['_id']),
            'name': updated['name'],
            'description': updated.get('description', ''),
            'style_id': 'classic-blue',
            'is_custom': True,
            'asset_url': updated.get('asset_url', ''),
            'asset_type': updated.get('asset_type', ''),
        }
    )


@router.delete('/restaurant/templates/{template_id}')
def delete_restaurant_template(template_id: str, current_user=Depends(get_current_user)):
    if not ObjectId.is_valid(template_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid template id')

    existing = templates_col.find_one({'_id': ObjectId(template_id), 'restaurant_id': current_user['_id']})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')

    templates_col.delete_one({'_id': ObjectId(template_id), 'restaurant_id': current_user['_id']})

    user_doc = current_user
    if current_user.get('template_id') == template_id:
        users_col.update_one({'_id': current_user['_id']}, {'$set': {'template_id': 'classic-blue'}})
        user_doc = users_col.find_one({'_id': current_user['_id']})

    return {'user': parse_user(user_doc)}


@router.put('/restaurant/template')
def set_template(payload: TemplateSelectionRequest, current_user=Depends(get_current_user)):
    selected = find_template_for_restaurant(current_user['_id'], payload.template_id)
    if not selected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid template id')

    users_col.update_one({'_id': current_user['_id']}, {'$set': {'template_id': selected['id']}})
    user = users_col.find_one({'_id': current_user['_id']})
    return {'user': parse_user(user)}
