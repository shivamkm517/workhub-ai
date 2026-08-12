from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app import security
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas import auth as auth_schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: auth_schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_data.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = security.hash_password(user_data.password)

    new_user = User(email=user_data.email, hashed_password=hashed)

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


@router.post("/refresh", response_model=auth_schemas.TokenResponse)
def refresh_token(payload: auth_schemas.RefreshTokenRequest, db: Session = Depends(get_db)):

    db_token = (db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token, RefreshToken.is_revoked == False).first())

    if not db_token or db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = security.create_access_token(data={"sub": db_token.user.email})

    return {
        "access_token": new_access_token,
        "refresh_token": db_token.token,
        "token_type": "bearer",
    }


@router.post("/reset-password")
def reset_password(data: auth_schemas.ResetPasswordSubmit, db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(
            data.token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

        email = payload.get("sub")
        purpose = payload.get("purpose")

        if email is None or purpose != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=400, detail="Expired or invalid token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = security.hash_password(data.new_password)

    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update(
        {"is_revoked": True}
    )

    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/forgot-password")
def forgot_password(data: auth_schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        return {"message": "If the email exists, a password reset link has been sent."}

    reset_token = security.create_password_reset_token(user.email)

    print(f"http://localhost:8000/reset-password?token={reset_token}")

    return {"message": "If the email exists, a password reset link has been sent."}


@router.post("/login", response_model=auth_schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    access_token = security.create_access_token(data={"sub": user.email})

    refresh_token = security.create_refresh_token(data={"sub": user.email})

    db_refresh_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(db_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(payload: auth_schemas.Logout, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    db_token = (
        db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token, RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked == False
        ).first()
    )

    if not db_token:
        raise HTTPException(
            status_code=400, detail="Token already revoked or not found"
        )

    db_token.is_revoked = True

    db.commit()

    return {"message": "Logged out successfully"}
