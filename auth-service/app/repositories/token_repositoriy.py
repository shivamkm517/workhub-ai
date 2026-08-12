from datetime import datetime

from sqlalchemy.orm import Session

from app.models.token import RefreshToken


class TokenRepository:

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken:

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=False,
        )

        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)

        return refresh_token

    @staticmethod
    def get_by_token(
        db: Session,
        token: str,
    ) -> RefreshToken | None:

        return (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token == token,
                RefreshToken.is_revoked.is_(False),
            )
            .first()
        )

    @staticmethod
    def revoke(
        db: Session,
        token: RefreshToken,
    ) -> None:

        token.is_revoked = True

        db.commit()

    @staticmethod
    def revoke_all_for_user(
        db: Session,
        user_id: int,
    ) -> None:

        (
            db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked.is_(False),
            )
            .update(
                {
                    RefreshToken.is_revoked: True
                },
                synchronize_session=False,
            )
        )

        db.commit()