from typing import Any, Dict

from bson import ObjectId
from fastapi import Header, HTTPException, status
from jose import jwt

from app.core.config import JWT_ALGORITHM, JWT_SECRET
from app.core.database import users_col


def get_current_user(authorization: str = Header(default='')) -> Dict[str, Any]:
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing bearer token')

    token = authorization.replace('Bearer ', '', 1).strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('sub')
        if not user_id or not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token payload')

        user = users_col.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token') from exc
