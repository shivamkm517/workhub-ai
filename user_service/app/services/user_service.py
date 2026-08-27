# user-service/app/services/user_service.py

from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    get_user_by_email,
    get_user_by_id
)


def find_user_by_email(
    db: Session,
    email: str
):
    return get_user_by_email(db, email)


def find_user_by_id(
    db: Session,
    user_id: int
):
    return get_user_by_id(db, user_id)