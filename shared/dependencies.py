from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import app.security as security
from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole

# 1. OAuth2 scheme initialization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 2. Database Session context manager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. Existing Authentication Dependency (Fixed imports and syntax)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credentials not valid",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Point directly to the imported User class from app.models.user
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

# 4. New Flexible RBAC Dependency Class
class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # Prevent deactivated users from performing actions
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="User account is deactivated"
            )
        # Verify role permissions
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to access this resource"
            )
        return current_user

