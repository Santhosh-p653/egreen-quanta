"""
auth.py — Authentication and JWT Security Layer for Egreen Quanta Admin Portal.
Implements bcrypt password hashing, JWT bearer tokens, user dependencies, and default admin seeding.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

SECRET_KEY = os.environ.get("JWT_SECRET", "egreen-quanta-secret-salt-key-2026-sih")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Computes bcrypt hash of a plaintext password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Decodes JWT and retrieves active user from database. Returns None if unauthenticated."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user


def require_admin(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """Enforces that caller is authenticated with the 'admin' role."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required for Admin access",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required",
        )
    return current_user


def seed_default_admin(db: Session):
    """Ensures at least one default administrator exists in the database."""
    admin_username = os.environ.get("DEFAULT_ADMIN_USER", "admin")
    admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123")

    existing = db.query(User).filter(User.username == admin_username).first()
    if not existing:
        admin_user = User(
            username=admin_username,
            email="admin@egreenquanta.gov.in",
            hashed_password=get_password_hash(admin_password),
            role="admin",
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        return admin_user
    return existing
