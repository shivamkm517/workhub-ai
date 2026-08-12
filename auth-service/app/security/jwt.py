from datetime import datetime, timedelta, timezone

from jose import jwt


SECRET_KEY = "workhub_jai_ho"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_TOKEN_EXPIRE_MINUTES = 10


def create_token(
    data: dict,
    expires_delta: timedelta,
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_access_token(data: dict) -> str:
    return create_token(
        data,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(data: dict) -> str:
    return create_token(
        data,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_password_reset_token(email: str) -> str:
    return create_token(
        {
            "sub": email,
            "purpose": "password_reset",
        },
        timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    )