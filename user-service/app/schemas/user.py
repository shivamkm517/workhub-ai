from pydantic import BaseModel, EmailStr,  Field
from typing import Optional
from app.models.user import UserRole


# shared attributes across schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

# Input schema for creating a new user (Registration)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 character long")
    role: Optional[UserRole] = UserRole.EMPLOYEE


# For reading user data safely ( No password is exposed )
class UserResponse(BaseModel):
    id: int
    email : EmailStr
    full_name: Optional[str] = None
    role : UserRole
    is_active: bool

    class Config:
        from_attributes = True

# For updating basic profiles ( self - service)
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None

# For administrative user management
class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# For activating / deactivating a user account
class UserStatusUpdate(BaseModel):
    is_active: bool

# For changing password when logged in
class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters long")
    
