import re
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.core.database import templates_col

MENU_TEMPLATES: List[Dict[str, Any]] = [
    {
        'id': 'classic-blue',
        'name': 'Classic Blue',
        'description': 'Bold blue section headers with clean menu rows.',
        'style_id': 'classic-blue',
        'is_custom': False,
        'asset_url': '',
        'asset_type': '',
    },
    {
        'id': 'slate-minimal',
        'name': 'Slate Minimal',
        'description': 'Minimal monochrome layout for modern bistros.',
        'style_id': 'slate-minimal',
        'is_custom': False,
        'asset_url': '',
        'asset_type': '',
    },
    {
        'id': 'warm-paper',
        'name': 'Warm Paper',
        'description': 'Soft paper-like tones with serif section titles.',
        'style_id': 'warm-paper',
        'is_custom': False,
        'asset_url': '',
        'asset_type': '',
    },
]
VALID_TEMPLATE_IDS = {tpl['id'] for tpl in MENU_TEMPLATES}


def normalize_template_name(name: str) -> str:
    return re.sub(r'\s+', ' ', name).strip()


def builtin_templates() -> List[Dict[str, Any]]:
    return [dict(tpl) for tpl in MENU_TEMPLATES]


def all_templates_for_restaurant(restaurant_id: ObjectId) -> List[Dict[str, Any]]:
    custom = []
    for doc in templates_col.find({'restaurant_id': restaurant_id}).sort([('name', 1)]):
        custom.append(
            {
                'id': str(doc['_id']),
                'name': doc['name'],
                'description': doc.get('description', ''),
                'style_id': 'custom-upload',
                'is_custom': True,
                'asset_url': doc.get('asset_url', ''),
                'asset_type': doc.get('asset_type', ''),
            }
        )
    return builtin_templates() + custom


def find_template_for_restaurant(restaurant_id: ObjectId, template_id: str) -> Optional[Dict[str, Any]]:
    builtin_map = {tpl['id']: tpl for tpl in builtin_templates()}
    if template_id in builtin_map:
        return builtin_map[template_id]

    if ObjectId.is_valid(template_id):
        custom = templates_col.find_one({'_id': ObjectId(template_id), 'restaurant_id': restaurant_id})
        if custom:
            return {
                'id': str(custom['_id']),
                'name': custom['name'],
                'description': custom.get('description', ''),
                'style_id': 'custom-upload',
                'is_custom': True,
                'asset_url': custom.get('asset_url', ''),
                'asset_type': custom.get('asset_type', ''),
            }
    return None
