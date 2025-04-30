"""Test cases for user login."""

from datetime import datetime, timedelta
from typing import Dict

from httpx import AsyncClient
import jwt
import pytest


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient, valid_user_data: Dict[str, str]
) -> None:
    """Test successful login."""
    # First create a user
    await client.post("/api/v1/users/signup", json=valid_user_data)

    # Try logging in
    login_data = {
        "username": valid_user_data["username"],
        "password": valid_user_data["password"],
    }
    response = await client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Verify token expiry (3 days)
    token = data["access_token"]

    # Verify token can be decoded with correct secret key
    from pennyorpound.core.security import SECRET_KEY

    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    exp = datetime.fromtimestamp(decoded["exp"])
    now = datetime.now()
    assert (
        timedelta(days=2, hours=23) < (exp - now) < timedelta(days=3, hours=1)
    )


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    client: AsyncClient, valid_user_data: Dict[str, str]
) -> None:
    """Test login with invalid credentials."""
    # First create a user
    await client.post("/api/v1/users/signup", json=valid_user_data)

    # Try logging in with wrong password
    login_data = {
        "username": valid_user_data["username"],
        "password": "wrongpassword",
    }
    response = await client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    # Try logging in with non-existent username
    login_data = {
        "username": "nonexistent",
        "password": valid_user_data["password"],
    }
    response = await client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_invalid_token_signature(
    client: AsyncClient, valid_user_data: Dict[str, str]
) -> None:
    """Test JWT token signature validation with wrong secret key."""
    # First create a user
    await client.post("/api/v1/users/signup", json=valid_user_data)

    # Try logging in
    login_data = {
        "username": valid_user_data["username"],
        "password": valid_user_data["password"],
    }
    response = await client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200
    data = response.json()

    # Verify token can't be decoded with wrong secret key
    token = data["access_token"]
    wrong_secret = "wrong-secret-key"
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, wrong_secret, algorithms=["HS256"])
