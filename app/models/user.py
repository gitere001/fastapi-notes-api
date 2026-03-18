from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
from sqlalchemy import Enum as SAEnum
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    full_name = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    profile_picture = Column(String, nullable=True)
    role = Column(
        SAEnum(UserRole, name="user_role"), default=UserRole.USER, nullable=False
    )

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")
