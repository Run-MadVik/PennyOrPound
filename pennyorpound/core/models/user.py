"""User model for the application."""

from datetime import datetime
from typing import Any, Dict, Optional, Union
from zoneinfo import ZoneInfo

from bson import ObjectId
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    GetJsonSchemaHandler,
)
from pydantic_core import CoreSchema, core_schema


class PyObjectId(ObjectId):
    """Custom type for handling MongoDB ObjectIds."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetJsonSchemaHandler
    ) -> CoreSchema:
        """Get Pydantic core schema."""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(
                                cls.validate
                            ),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                str, return_schema=core_schema.str_schema()
            ),
        )

    @classmethod
    def validate(cls, v: Union[str, ObjectId]) -> ObjectId:
        """Validate and convert string to ObjectId.

        Args:
            v: Value to validate and convert.

        Returns:
            ObjectId: Converted ObjectId instance.

        Raises:
            ValueError: If the value is not a valid ObjectId.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, field_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        field_schema.update(type="string")
        return field_schema


class UserBase(BaseModel):
    """Base User model with common fields."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username"
    )
    first_name: str = Field(
        ..., min_length=1, max_length=50, description="First name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, description="Last name"
    )
    is_active: bool = Field(
        default=True, description="Whether the user is active"
    )
    is_verified: bool = Field(
        default=False, description="Whether the user's email is verified"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("UTC")),
        description="Account creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("UTC")),
        description="Last update timestamp",
    )


class UserCreate(UserBase):
    """User model for creation with password."""

    password: str = Field(..., min_length=8, description="User's password")


class UserUpdate(BaseModel):
    """User model for updates."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserInDB(UserBase):
    """User model as stored in database."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str = Field(..., description="Hashed password")

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert model to dictionary and handle ObjectId."""
        dict_repr = super().model_dump(*args, **kwargs)
        dict_repr["id"] = str(dict_repr.pop("_id"))
        return dict_repr


class UserResponse(UserBase):
    """User model for API responses."""

    id: str = Field(..., description="User ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-04-29T00:00:00Z",
                "updated_at": "2024-04-29T00:00:00Z",
            }
        }
    )
