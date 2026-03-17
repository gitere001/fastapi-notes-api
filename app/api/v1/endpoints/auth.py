from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserOut,
             status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).register(data)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return AuthService(db).login(data.email, data.password)
