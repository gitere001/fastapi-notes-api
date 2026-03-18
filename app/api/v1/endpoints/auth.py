from fastapi import APIRouter, Depends, status, Request, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserOut,
    LoginResponse,
    AdminUserCreate,
)
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).register(data)


@router.post(
    "/register-admin", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
def register_admin(
    data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    return AuthService(db).create_admin_user(data)


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    return await AuthService(db).login(data.email, data.password, response)


@router.post("/logout", response_model=LoginResponse)
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    return await AuthService(db).logout(request, response)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
