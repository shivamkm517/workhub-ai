from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.token_repository import TokenRepository
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.security.password import verify_password


class AuthService:

    @staticmethod
    def generate_tokens(
        db: Session,
        user_id: int,
    ) -> dict:
        """
        Generate access and refresh tokens for a user.
        """

        access_token = create_access_token(
            {
                "sub": str(user_id),
                "type": "access",
            }
        )

        refresh_token = create_refresh_token(
            {
                "sub": str(user_id),
                "type": "refresh",
            }
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=7)
        )

        TokenRepository.create(
            db=db,
            user_id=user_id,
            token=refresh_token,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def logout(
        db: Session,
        refresh_token: str,
    ) -> None:
        """
        Revoke a refresh token.
        """

        token = TokenRepository.get_by_token(
            db,
            refresh_token,
        )

        if token is None:
            return

        TokenRepository.revoke(
            db,
            token,
        )