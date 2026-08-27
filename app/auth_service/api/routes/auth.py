from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth_service.schemas import auth as auth_schemas
from app.auth_service.services.auth_service import AuthService
from app.shared.dependencies import get_db, get_current_user

from app.shared.exception.auth import (
    EmailAlreadyRegisteredError,
    InvalidCredentialError,
    InactiveUserError,
    InvalidRefreshTokenError,
    InvalidPasswordResetTokenError,
    UserNotFoundError,
)
from app.user_service.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: auth_schemas.UserRegister,
    db: Session = Depends(get_db)
):

    try:
        return AuthService.register_user(
            db,
            user_data
        )

    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )


@router.post(
    "/login",
    response_model=auth_schemas.TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    try:
        return AuthService.login_user(
            db,
            form_data.username,
            form_data.password
        )

    except InvalidCredentialError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )


@router.post(
    "/refresh-token",
    response_model=auth_schemas.TokenResponse
)
def refresh_token(
    payload: auth_schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):

    try:
        return AuthService.refresh_access_token(
            db,
            payload.refresh_token
        )

    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

@router.post(
    "/forgot-password",
    response_model=auth_schemas.ForgotPasswordResponse
)
def forgot_password(
    data: auth_schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    try:
        return AuthService.forgot_password(
            db,
            data.email
        )

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post("/reset-password")
def reset_password(
    data: auth_schemas.ResetPasswordSubmit,
    db: Session = Depends(get_db)
):

    try:
        return AuthService.reset_password(
            db,
            data.token,
            data.new_password
        )

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    except InvalidPasswordResetTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired password reset token"
        )


@router.post("/logout")
def logout(
    payload: auth_schemas.Logout,
    db: Session = Depends(get_db)
):

    try:
        return AuthService.logout_user(
            db,
            payload.refresh_token
        )

    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

@router.post("/change-password")
def change_password(
    data: auth_schemas.ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return AuthService.change_password(
            db,
            current_user,
            data.old_password,
            data.new_password
        )

    except InvalidCredentialError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password"
        )