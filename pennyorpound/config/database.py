"""Database configuration and connection management."""

import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .logging import logger

load_dotenv()


class DatabaseConfig:
    """Database configuration class."""

    def __init__(self) -> None:
        """Initialize database configuration."""
        self.username = os.getenv("MONGODB_USERNAME")
        self.password = os.getenv("MONGODB_PASSWORD")
        self.url = os.getenv("MONGODB_URL")
        self.app_name = os.getenv("MONGODB_APPNAME", "PennyOrPound")

    @property
    def connection_string(self) -> str:
        """Get the MongoDB connection string."""
        return (
            f"mongodb+srv://{self.username}:{self.password}"
            f"@{self.url}/?w=majority&appName={self.app_name}"
        )


async def setup_mongodb_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create MongoDB indexes."""
    await db.users.create_index([("email", 1)], unique=True, background=True)
    await db.users.create_index([("username", 1)], unique=True, background=True)
    logger.info("MongoDB indexes created successfully")


# Create a global client instance
config = DatabaseConfig()
client: AsyncIOMotorClient = AsyncIOMotorClient(config.connection_string)


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Database dependency for FastAPI."""
    try:
        await client.admin.command("ping")
        db = client[config.app_name]
        await setup_mongodb_indexes(db)
        yield db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise
