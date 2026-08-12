from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import security
from app.dependencies import RoleChecker, get_current_user, get_db
from app.models.user import User, UserRole
from app.models.token import RefreshToken
from app.schemas import user as user_schemas
from app.services.audit_service import log_event

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Permissions
admin_only = RoleChecker([UserRole.ADMINISTRATOR])
admin_or_manager = RoleChecker([UserRole.ADMINISTRATOR, UserRole.MANAGER])


# ------------------------------------------------------------------
# CREATE USER
# ------------------------------------------------------------------
@router.post("", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: user_schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    """Create a new user (Administrator only)."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed = security.hash_password(user_data.password)
    role = user_data.role or UserRole.EMPLOYEE

    new_user = User(
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        role=role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_event(
        db=db,
        action="USER_CREATE",
        user_id=current_user.id,
        entity_type="User",
        entity_id=new_user.id,
        details=f"Created user '{new_user.email}' with role '{role.value}'"
    )

    return new_user


# ------------------------------------------------------------------
# VIEW / LIST USERS
# ------------------------------------------------------------------
@router.get("/me", response_model=user_schemas.UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """View the currently authenticated user's own profile."""
    return current_user


@router.get("", response_model=List[user_schemas.UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by email or full name"),
    role_filter: Optional[UserRole] = Query(None, alias="role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_manager)
):
    """List and search users with pagination and filtering (Admin/Manager)."""
    query = db.query(User)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (User.email.ilike(pattern)) | (User.full_name.ilike(pattern))
        )
    if role_filter:
        query = query.filter(User.role == role_filter)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.order_by(User.id.asc()).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=user_schemas.UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_manager)
):
    """View details of a single user (Admin/Manager)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# ------------------------------------------------------------------
# UPDATE PROFILE (self-service)
# ------------------------------------------------------------------
@router.put("/me", response_model=user_schemas.UserResponse)
def update_my_profile(
    profile_data: user_schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the current user's own profile (self-service)."""
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", status_code=status.HTTP_200_OK)
def change_my_password(
    password_data: user_schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change the current user's password (requires old password)."""
    if not security.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    current_user.hashed_password = security.hash_password(password_data.new_password)

    # Revoke all existing refresh tokens for security
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})

    db.commit()

    log_event(
        db=db,
        action="USER_PASSWORD_CHANGE",
        user_id=current_user.id,
        entity_type="User",
        entity_id=current_user.id
    )

    return {"message": "Password changed successfully"}


# ------------------------------------------------------------------
# UPDATE USER (admin)
# ------------------------------------------------------------------
@router.put("/{user_id}", response_model=user_schemas.UserResponse)
def update_user(
    user_id: int,
    update_data: user_schemas.UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    """Update a user's details (Administrator only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.role is not None:
        user.role = update_data.role
    if update_data.is_active is not None:
        user.is_active = update_data.is_active

    db.commit()
    db.refresh(user)

    log_event(
        db=db,
        action="USER_UPDATE",
        user_id=current_user.id,
        entity_type="User",
        entity_id=user.id,
        details=f"Updated user '{user.email}'"
    )

    return user


# ------------------------------------------------------------------
# ACTIVATE / DEACTIVATE USER
# ------------------------------------------------------------------
@router.patch("/{user_id}/status", response_model=user_schemas.UserResponse)
def set_user_status(
    user_id: int,
    status_data: user_schemas.UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    """Activate or deactivate a user account (Administrator only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    user.is_active = status_data.is_active

    # If deactivating, revoke all refresh tokens so the user is logged out
    if not status_data.is_active:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})

    db.commit()
    db.refresh(user)

    log_event(
        db=db,
        action="USER_DEACTIVATE" if not status_data.is_active else "USER_ACTIVATE",
        user_id=current_user.id,
        entity_type="User",
        entity_id=user.id,
        details=f"Set user '{user.email}' active={status_data.is_active}"
    )

    return user


# ------------------------------------------------------------------
# DELETE USER
# ------------------------------------------------------------------
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    """Delete a user account (Administrator only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )

    email = user.email

    # Revoke all refresh tokens before deleting
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()

    db.delete(user)
    db.commit()

    log_event(
        db=db,
        action="USER_DELETE",
        user_id=current_user.id,
        entity_type="User",
        entity_id=user_id,
        details=f"Deleted user '{email}'"
    )

    return {"message": f"User '{email}' deleted successfully"}
