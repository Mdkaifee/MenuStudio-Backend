from typing import Any, Dict

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_SPECIALS = set("!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~\\")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    restaurant_name: str = Field(min_length=2, max_length=25)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator('restaurant_name')
    @classmethod
    def validate_restaurant_name(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) > 25:
            raise ValueError('Restaurant name must be 25 characters or fewer')
        if len(cleaned) < 2:
            raise ValueError('Restaurant name must be at least 2 characters')
        return cleaned

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        has_upper = any(ch.isupper() for ch in value)
        has_lower = any(ch.islower() for ch in value)
        has_digit = any(ch.isdigit() for ch in value)
        has_special = any(ch in PASSWORD_SPECIALS for ch in value)
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError('Password must include uppercase, lowercase, number, and special character')
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class AuthResponse(BaseModel):
    access_token: str
    user: Dict[str, Any]


class RegisterResponse(BaseModel):
    message: str
