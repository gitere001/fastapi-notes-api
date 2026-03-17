from fastapi import Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import (
    decode_access_token,
    decode_refresh_token,
    create_access_token,
    create_refresh_token,
)
from app.db.redis import get_redis
from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.services.auth_service import (
    COOKIE_CONFIG,
    REFRESH_TOKEN_MAX_AGE,
    ACCESS_TOKEN_MAX_AGE,
)
import json


async def get_current_user(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    access_token = request.cookies.get("accessToken")
    refresh_token = request.cookies.get("refreshToken")

    if not access_token and not refresh_token:
        raise credentials_exception

    if access_token:
        payload = decode_access_token(access_token)
        if payload:
            email = payload.get("sub")
            if email:
                user = UserRepository(db).get_by_email(email)
                if user and user.is_active:
                    return user

    if not refresh_token:
        raise credentials_exception

    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise credentials_exception

    jti = payload.get("jti")
    email = payload.get("sub")

    if not jti or not email:
        raise credentials_exception

    user = UserRepository(db).get_by_email(email)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    redis = await get_redis()
    stored = await redis.get(f"refresh_token:{user.id}:{jti}")
    if not stored:
        response.delete_cookie("accessToken")
        response.delete_cookie("refreshToken")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or token reused",
        )

    await redis.delete(f"refresh_token:{user.id}:{jti}")

    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token, new_jti = create_refresh_token(data={"sub": user.email})

    await redis.setex(
        f"refresh_token:{user.id}:{new_jti}",
        REFRESH_TOKEN_MAX_AGE,
        json.dumps({"jti": new_jti, "user_id": user.id}),
    )

    response.set_cookie(
        key="accessToken",
        value=new_access_token,
        max_age=ACCESS_TOKEN_MAX_AGE,
        **COOKIE_CONFIG,
    )
    response.set_cookie(
        key="refreshToken",
        value=new_refresh_token,
        max_age=REFRESH_TOKEN_MAX_AGE,
        **COOKIE_CONFIG,
    )

    return user
