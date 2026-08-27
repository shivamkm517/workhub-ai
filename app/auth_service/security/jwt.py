from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.shared.exception.auth import InvalidPasswordResetTokenError
from app.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    RESET_TOKEN_EXPIRE_MINUTES
)
import uuid


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
    data = {**data, "type": "access"}

    return create_token(
        data,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(data: dict) -> str:
    data = {**data, "type": "refresh"}

    return create_token(
        data,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )




def create_password_reset_token(email: str) -> str:

    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": email,
        "purpose": "password_reset",
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_password_reset_token(token: str) -> dict:

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("purpose") != "password_reset":
            raise ValueError("Invalid token purpose")

        if payload.get("sub") is None:
            raise ValueError("Invalid token")

        return payload

    except (JWTError, ValueError):
        raise InvalidPasswordResetTokenError(
            "Invalid or expired password reset token"
        )

def decode_access_token(token: str) -> dict:

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    if payload.get("type") != "access":
        raise JWTError("Invalid token type")

    return payload