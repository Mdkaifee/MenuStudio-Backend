import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import JWT_ALGORITHM, JWT_EXP_DAYS, JWT_SECRET


def hash_password(password: str, salt: bytes) -> str:
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 120_000)
    return base64.b64encode(hashed).decode('utf-8')


def build_password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    return f"{base64.b64encode(salt).decode('utf-8')}:{hash_password(password, salt)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_b64, hash_b64 = stored_hash.split(':', 1)
        salt = base64.b64decode(salt_b64)
        computed = hash_password(password, salt)
        return hmac.compare_digest(computed, hash_b64)
    except Exception:
        return False


def create_token(user_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS)
    payload = {'sub': user_id, 'exp': exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
