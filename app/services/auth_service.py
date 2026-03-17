from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate
from app.core.security import verify_password, create_access_token
from app.models.user import User


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

    def login(self, email: str, password: str) -> dict:
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
                detail="Account is deactivated"
            )
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
