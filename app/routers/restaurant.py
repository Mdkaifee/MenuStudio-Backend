from fastapi import APIRouter, Depends

from app.core.config import FRONTEND_BASE_URL
from app.core.qr import generate_qr_data_url
from app.dependencies.auth import get_current_user

router = APIRouter(prefix='/restaurant', tags=['restaurant'])


@router.get('/qr')
def restaurant_qr(current_user=Depends(get_current_user)):
    url = f"{FRONTEND_BASE_URL}/menu/{str(current_user['_id'])}"
    return {
        'target_url': url,
        'qr_data_url': generate_qr_data_url(url),
    }
