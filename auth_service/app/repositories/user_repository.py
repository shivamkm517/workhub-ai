from sqlalchemy.orm import Session

from user_service.models.user import User


class UserRepository:

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ):

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )


    @staticmethod
    def create(
        db: Session,
        user: User
    ):

        db.add(user)
        db.commit()
        db.refresh(user)

        return user


    @staticmethod
    def password_update(
        db: Session,
        user: User,
        hashed_password: str
    ):

        user.hashed_password = hashed_password

        db.commit()
        db.refresh(user)

        return user