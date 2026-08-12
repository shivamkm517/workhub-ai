import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.database import Base
from sqlalchemy.orm import relationship

class UserRole(str, enum.Enum):
    ADMINISTRATOR = "administrator"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user")