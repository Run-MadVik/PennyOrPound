"""User-related API endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from ...config.database import get_db
from ...core.models.user import UserCreate, UserLogin, UserResponse
from ...core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_by_identifier(
    db: AsyncIOMotorDatabase, identifier: str
) -> Optional[Dict[str, Any]]:
    """Get a user by email or username."""
    return await db.users.find_one(
        {"$or": [{"email": identifier}, {"username": identifier}]}
    )


@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(
    user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)
) -> UserResponse:
    """
    Create a new user.

    Args:
        user: The user data for registration
        db: MongoDB database instance

    Returns:
        The created user data

    Raises:
        HTTPException: If email or username already exists
    """
    # Check if user exists with either email or username in a single query
    existing_user = await db.users.find_one(
        {"$or": [{"email": user.email}, {"username": user.username}]}
    )

    if existing_user:
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=400, detail="Email already registered"
            )
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user document
    user_dict = user.model_dump()
    hashed_password = get_password_hash(user_dict.pop("password"))
    user_dict["hashed_password"] = hashed_password

    try:
        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": result.inserted_id})
        if created_user:
            # Convert _id to string id for the response
            created_user["id"] = str(created_user.pop("_id"))
            return UserResponse(**created_user)
        raise HTTPException(status_code=500, detail="Failed to create user")
    except DuplicateKeyError:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists",
        )


@router.post("/login")
async def login(
    user_credentials: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)
) -> Dict[str, str]:
    """
    Authenticate a user and return a JWT token.

    Args:
        user_credentials: The login credentials
        db: MongoDB database instance

    Returns:
        Dict containing the access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by username or email
    user = await get_user_by_identifier(db, user_credentials.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token
    token_data = {"sub": str(user["_id"]), "username": user["username"]}
    access_token = create_access_token(token_data)

    return {"access_token": access_token, "token_type": "bearer"}
