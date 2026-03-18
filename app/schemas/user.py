from pydantic import BaseModel, EmailStr, field_validator
from app.models.enums import UserRole
from datetime import datetime
import re


def validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", value):
        raise ValueError("Password must contain at least one special character")
    if re.search(r"\s", value):
        raise ValueError("Password cannot contain spaces")
    blocked = ["password", "password123", "admin123", "12345678", "qwerty123"]
    if value.lower() in blocked:
        raise ValueError("Password is too common")
    return value


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.USER

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    full_name: str
    last_login: datetime | None = None
    profile_picture: str | None = None
    role: UserRole

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    success: bool
    message: str
