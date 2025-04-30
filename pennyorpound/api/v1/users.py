"""User-related API endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from ...config.database import get_db
from ...core.models.user import UserCreate, UserResponse
from ...core.security import get_password_hash

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
