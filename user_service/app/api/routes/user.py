# user-service/app/api/routes/user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user_service import find_user_by_email
from app.schemas.user import UserAuthResponse


router = APIRouter(
    prefix="/internal/users",
    tags=["Internal Users"]
)


@router.get(
    "/by-email/{email}",
    response_model=UserAuthResponse
)
def get_user_for_auth(
    email: str,
    db: Session = Depends(get_db)
):
    user = find_user_by_email(db, email)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return UserAuthResponse(
        id=user.id,
        email=user.email,
        password=user.password
    )