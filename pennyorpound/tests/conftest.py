"""Test configuration and fixtures."""

from collections.abc import Coroutine
import os
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, cast

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pytest
import pytest_asyncio

from pennyorpound.app import app
from pennyorpound.config.database import (
    DatabaseConfig,
    get_db,
    setup_mongodb_indexes,
)


class DatabaseTestConfig(DatabaseConfig):
    """Database configuration for testing."""

    def __init__(self) -> None:
        """Initialize test database configuration."""
        self.username = os.getenv("MONGODB_TEST_USERNAME")
        self.password = os.getenv("MONGODB_TEST_PASSWORD")
        self.url = os.getenv("MONGODB_TEST_URL")
        self.app_name = os.getenv("MONGODB_TEST_APPNAME", "PennyOrPoundTest")


@pytest.fixture(name="test_config")
def test_config_fixture() -> DatabaseTestConfig:
    """Create test database config."""
    return DatabaseTestConfig()


@pytest_asyncio.fixture(name="mongo_client")
async def mongo_client_fixture(
    test_config: DatabaseTestConfig,
) -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create test MongoDB client."""
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        test_config.connection_string
    )
    try:
        await client.admin.command("ping")
        yield client
    finally:
        if client:
            client.close()


@pytest_asyncio.fixture(name="test_db")
async def test_db_fixture(
    mongo_client: AsyncIOMotorClient,
    test_config: DatabaseTestConfig,
) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create test database with proper cleanup."""
    db_name = test_config.app_name
    db = mongo_client[db_name]
    await setup_mongodb_indexes(db)

    try:
        yield db
    finally:
        await mongo_client.drop_database(db_name)


@pytest_asyncio.fixture(name="test_app")
async def test_app_fixture(
    test_db: AsyncIOMotorDatabase,
) -> AsyncGenerator[FastAPI, None]:
    """Create test application with real test database."""

    async def get_test_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
        yield test_db

    app.dependency_overrides = {get_db: get_test_db}
    yield app
    app.dependency_overrides = {}


@pytest_asyncio.fixture(name="client")
async def client_fixture(
    test_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    app_handler = cast(
        Callable[
            [
                Dict[str, Any],
                Callable[[], Awaitable[Dict[str, Any]]],
                Callable[[Dict[str, Any]], Coroutine[None, None, None]],
            ],
            Coroutine[None, None, None],
        ],
        test_app,
    )
    transport = ASGITransport(app=app_handler)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(name="valid_user_data")
def valid_user_data_fixture() -> Dict[str, str]:
    """Create valid user test data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
    }
