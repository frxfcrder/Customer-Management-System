import hashlib
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency: Authentication Service (JWT + Password Hashing)
class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "change-me-to-a-long-random-secret")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.token_expires = timedelta(
            minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        )

    def hash_password(self, password: str) -> str:
        # Placeholder SHA256 (swap for bcrypt/argon2 in prod)
        return hashlib.sha256(f"{password}{self.secret_key}".encode()).hexdigest()

    def get_password_hash(self, password: str) -> str:
        return self.hash_password(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return self.hash_password(plain) == hashed

    def token_valid(self, email: str) -> bool:
        return bool(email and "@" in email)

    def generate_token(self, email: str, name: str = "") -> dict:
        """Generate JWT token"""
        if not self.token_valid(email):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        expire = datetime.now(timezone.utc) + self.token_expires
        data = {
            "sub": email,
            "email": email,
            "name": name,
            "exp": expire,
        }
        token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
        return {"access_token": token, "token_type": "bearer"}

    def verify_token(self, token: str) -> dict | None:
        """Verify JWT token for authentication"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def authenticate_user(self, email: str, password: str) -> tuple[bool, str]:
        """Authenticate user and validate email/password"""
        # TODO: look up user in DB and check hash
        if not self.token_valid(email) or not password:
            return False, "Invalid credentials"
        return True, "authenticated"

    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> dict:
        payload = self.verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return payload
