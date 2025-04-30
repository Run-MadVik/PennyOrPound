"""Security utilities for the application."""

from datetime import datetime, timedelta
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
import jwt
from passlib.context import CryptContext

load_dotenv()

# JWT settings
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-secret-key-here"
)  # Fallback for development only
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", "3"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    hashed_password: str = pwd_context.hash(password)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(ZoneInfo("UTC")) + timedelta(
        days=ACCESS_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
