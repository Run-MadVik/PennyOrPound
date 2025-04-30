"""Test cases for user-related endpoints."""

from typing import Dict

from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
import pytest


@pytest.mark.asyncio
async def test_create_user(
    client: AsyncClient,
    valid_user_data: Dict[str, str],
    test_db: AsyncIOMotorDatabase,
) -> None:
    """Test user creation endpoint."""
    response = await client.post("/api/v1/users/signup", json=valid_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == valid_user_data["email"]
    assert "password" not in data
    assert "hashed_password" not in data

    # Verify user was actually created in database
    user = await test_db.users.find_one({"email": valid_user_data["email"]})
    assert user is not None
    assert user["username"] == valid_user_data["username"]


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    client: AsyncClient,
    valid_user_data: Dict[str, str],
    test_db: AsyncIOMotorDatabase,
) -> None:
    """Test user creation with duplicate email."""
    # First create a user
    response = await client.post("/api/v1/users/signup", json=valid_user_data)
    assert response.status_code == 201

    # Try to create another user with the same email
    response = await client.post("/api/v1/users/signup", json=valid_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

    # Verify only one user exists
    count = await test_db.users.count_documents(
        {"email": valid_user_data["email"]}
    )
    assert count == 1


@pytest.mark.asyncio
async def test_create_user_duplicate_username(
    client: AsyncClient,
    valid_user_data: Dict[str, str],
    test_db: AsyncIOMotorDatabase,
) -> None:
    """Test user creation with duplicate username."""
    # First create a user
    response = await client.post("/api/v1/users/signup", json=valid_user_data)
    assert response.status_code == 201

    # Try to create another user with same username but different email
    new_user_data = valid_user_data.copy()
    new_user_data["email"] = "another@example.com"
    response = await client.post("/api/v1/users/signup", json=new_user_data)
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]

    # Verify only one user exists with the username
    count = await test_db.users.count_documents(
        {"username": valid_user_data["username"]}
    )
    assert count == 1


@pytest.mark.asyncio
async def test_create_user_invalid_data(
    client: AsyncClient, test_db: AsyncIOMotorDatabase
) -> None:
    """Test user creation with invalid data."""
    invalid_data = {
        "email": "invalid-email",
        "username": "t",  # too short
        "password": "short",  # too short
        "first_name": "",  # empty
        "last_name": "",  # empty
    }
    response = await client.post("/api/v1/users/signup", json=invalid_data)
    assert response.status_code == 422  # Validation error

    # Verify no user was created
    count = await test_db.users.count_documents({})
    assert count == 0
