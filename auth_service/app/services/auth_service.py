from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.security import jwt, password

from app.repositories.user_repository import (
    UserRepository
)

from app.repositories.token_repository import (
    TokenRepository
)

from user_service.app.models.user import User

from shared.exception.auth import (
    EmailAlreadyRegisteredError,
    InvalidRefreshTokenError,
    UserNotFoundError,
    InactiveUserError,
    InvalidCredentialError,
)


class AuthService:

    @staticmethod
    def register_user(
        db: Session,
        user_data
    ):

        db_user = UserRepository.get_by_email(
            db,
            user_data.email
        )

        if db_user:
            raise EmailAlreadyRegisteredError()

        hashed_password = password.hash_password(
            user_data.password
        )

        user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )

        UserRepository.create(
            db,
            user
        )

        return {
            "message": "User registered successfully"
        }


    @staticmethod
    def login_user(
        db: Session,
        email: str,
        plain_password: str
    ):

        user = UserRepository.get_by_email(
            db,
            email
        )

        if not user:
            raise InvalidCredentialError()

        if not password.verify_password(
            plain_password,
            user.hashed_password
        ):
            raise InvalidCredentialError()

        if not user.is_active:
            raise InactiveUserError()

        access_token = jwt.create_access_token(
            data={
                "sub": user.email
            }
        )

        refresh_token = jwt.create_refresh_token(
            data={
                "sub": user.email
            }
        )

        TokenRepository.create(
            db=db,
            token=refresh_token,
            user_id=user.id
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str
    ):

        db_token = TokenRepository.get_valid_token(
            db,
            refresh_token
        )

        if not db_token:
            raise InvalidRefreshTokenError()

        expires_at = db_token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at < datetime.now(timezone.utc):
            raise InvalidRefreshTokenError()

        user = db_token.user

        new_access_token = jwt.create_access_token(
            data={
                "sub": user.email
            }
        )

        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def forgot_password(
        db: Session,
        email: str
    ):

        user = UserRepository.get_by_email(
            db,
            email
        )

        if not user:
            raise UserNotFoundError()

        reset_token = jwt.create_password_reset_token(
            user.email
        )

        return {
            "message": "Password reset token generated",
            "reset_token": reset_token
        }


    @staticmethod
    def reset_password(
        db: Session,
        token: str,
        new_password: str
    ):

        payload = jwt.decode_password_reset_token(
            token
        )

        email = payload.get("sub")

        user = UserRepository.get_by_email(
            db,
            email
        )

        if not user:
            raise UserNotFoundError()

        hashed_password = password.hash_password(
            new_password
        )

        UserRepository.password_update(
            db,
            user,
            hashed_password
        )

        TokenRepository.revoke_user_tokens(
            db,
            user.id
        )

        return {
            "message": "Password reset successfully"
        }

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        old_password: str,
        new_password: str
    ):

        # 1. Verify old password
        if not password.verify_password(
            old_password,
            user.hashed_password
        ):
            raise InvalidCredentialError()

        # 2. Hash new password
        new_hashed_password = password.hash_password(
            new_password
        )

        # 3. Update password
        UserRepository.password_update(
            db,
            user,
            new_hashed_password
        )

        # 4. Revoke existing refresh tokens
        TokenRepository.revoke_user_tokens(
            db,
            user.id
        )

        return {
            "message": "Password changed successfully"
        }

    @staticmethod
    def logout_user(
        db: Session,
        refresh_token: str
    ):

        db_token = TokenRepository.get_valid_token(
            db,
            refresh_token
        )

        if not db_token:
            raise InvalidRefreshTokenError()

        TokenRepository.revoke(
            db,
            db_token
        )

        return {
            "message": "Logged out successfully"
        }


   