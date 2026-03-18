from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Request
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, AdminUserCreate
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.db.redis import get_redis
from app.models.user import User
import json


COOKIE_CONFIG = {
    "httponly": True,
    "samesite": settings.COOKIE_SAMESITE,
    "secure": settings.COOKIE_SECURE,
}

ACCESS_TOKEN_MAX_AGE = 15 * 60
REFRESH_TOKEN_MAX_AGE = 6 * 60 * 60


class AuthService:

    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        if self.repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        return self.repo.create(data)

    def create_admin_user(self, data: AdminUserCreate) -> User:
        if self.repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        return self.repo.create(data, role=data.role)

    async def login(self, email: str, password: str, response: Response) -> dict:

        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        access_token = create_access_token(data={"sub": user.email})
        refresh_token, jti = create_refresh_token(data={"sub": user.email})

        redis = await get_redis()
        await redis.setex(
            f"refresh_token:{user.id}:{jti}",
            REFRESH_TOKEN_MAX_AGE,
            json.dumps(
                {
                    "jti": jti,
                    "user_id": user.id,
                }
            ),
        )

        response.set_cookie(
            key="accessToken",
            value=access_token,
            max_age=ACCESS_TOKEN_MAX_AGE,
            **COOKIE_CONFIG,
        )
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            max_age=REFRESH_TOKEN_MAX_AGE,
            **COOKIE_CONFIG,
        )

        return {"success": True, "message": "Login successful"}

    async def logout(self, request: Request, response: Response) -> dict:
        refresh_token = request.cookies.get("refreshToken")

        if refresh_token:
            from app.core.security import decode_refresh_token

            payload = decode_refresh_token(refresh_token)
            if payload:
                jti = payload.get("jti")
                email = payload.get("sub")
                if jti and email:
                    user = self.repo.get_by_email(email)
                    if user:
                        redis = await get_redis()
                        await redis.delete(f"refresh_token:{user.id}:{jti}")

        response.delete_cookie("accessToken")
        response.delete_cookie("refreshToken")

        return {"success": True, "message": "Logout successful"}
