import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.auth_service.models.token import RefreshToken
from app.config import REFRESH_TOKEN_EXPIRE_DAYS


class TokenRepository:

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()


    @staticmethod
    def create(
        db: Session,
        token: str,
        user_id: int
    ):

        token_hash = TokenRepository.hash_token(token)

        db_refresh_token = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(
                    days=REFRESH_TOKEN_EXPIRE_DAYS
                )
            )
        )

        db.add(db_refresh_token)
        db.commit()
        db.refresh(db_refresh_token)

        return db_refresh_token


    @staticmethod
    def get_valid_token(
        db: Session,
        token: str
    ):

        token_hash = TokenRepository.hash_token(token)

        return (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False
            )
            .first()
        )


    @staticmethod
    def revoke(
        db: Session,
        refresh_token: RefreshToken
    ):

        refresh_token.revoked = True

        db.commit()
        db.refresh(refresh_token)

        return refresh_token


    @staticmethod
    def revoke_user_tokens(
        db: Session,
        user_id: int
    ):

        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).update(
            {
                "revoked": True
            },
            synchronize_session=False
        )

        db.commit()