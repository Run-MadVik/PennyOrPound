"""Security utilities for the application."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    hashed_password: str = pwd_context.hash(password)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result
