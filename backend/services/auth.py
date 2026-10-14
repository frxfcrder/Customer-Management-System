import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from models.user import User
from services.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# Dependency: Authentication Service (JWT + bcrypt password hashing)
class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "change-me-to-a-long-random-secret")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.token_expires = timedelta(
            minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        )

    # --- passwords ---
    def hash_password(self, password: str) -> str:
        """Hash a password with bcrypt (per-password salt included)."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def get_password_hash(self, password: str) -> str:
        return self.hash_password(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        """Constant-time comparison of a plain password against its bcrypt hash."""
        if not plain or not hashed:
            return False
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except ValueError:
            return False

    # --- tokens ---
    def token_valid(self, email: str) -> bool:
        return bool(email and "@" in email)

    def generate_token(
        self, email: str, name: str = "", user_id: int | None = None
    ) -> dict:
        """Generate a JWT for an authenticated user."""
        if not self.token_valid(email):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        expire = datetime.now(timezone.utc) + self.token_expires
        data = {
            "sub": str(user_id) if user_id is not None else email,
            "user_id": user_id,
            "email": email,
            "name": name,
            "exp": expire,
        }
        token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
        return {"access_token": token, "token_type": "bearer"}

    def verify_token(self, token: str) -> dict | None:
        """Verify JWT token, returning its payload (or None if invalid/expired)."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None

    # --- users ---
    def create_user(self, db: Session, email: str, password: str, name: str = "") -> User:
        """Create a new user with a hashed password (caller commits)."""
        user = User(name=name or None, email=email, password_hash=self.hash_password(password))
        db.add(user)
        return user

    def authenticate_user(self, db: Session, email: str, password: str) -> User | None:
        """Check credentials against the users table; returns the user or None."""
        user = db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user

    # --- FastAPI dependency ---
    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        """Resolve the authenticated user from the bearer token, or raise 401."""
        credentials_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = self.verify_token(token)
        if payload is None:
            raise credentials_error

        identifier = payload.get("email") or payload.get("sub")
        if not identifier:
            raise credentials_error

        user: User | None
        user_id = payload.get("user_id")
        if isinstance(user_id, int):
            user = db.get(User, user_id)
        else:
            user = db.query(User).filter(User.email == identifier).first()

        if user is None:
            raise credentials_error
        return user
