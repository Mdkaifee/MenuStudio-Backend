from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import users_col
from app.core.security import build_password_hash, create_token, verify_password
from app.dependencies.auth import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, RegisterResponse
from app.services.serializers import parse_user

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> RegisterResponse:
    if users_col.find_one({'email': payload.email.lower()}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')

    user_doc = {
        'email': payload.email.lower(),
        'password_hash': build_password_hash(payload.password),
        'restaurant_name': payload.restaurant_name.strip(),
        'template_id': 'classic-blue',
        'created_at': datetime.now(timezone.utc),
    }
    users_col.insert_one(user_doc)
    return RegisterResponse(message='Registered successfully. Please login.')


@router.post('/login', response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    user = users_col.find_one({'email': payload.email.lower()})
    if not user or not verify_password(payload.password, user.get('password_hash', '')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    token = create_token(str(user['_id']))
    return AuthResponse(access_token=token, user=parse_user(user))


@router.get('/me')
def me(current_user=Depends(get_current_user)):
    return {'user': parse_user(current_user)}
