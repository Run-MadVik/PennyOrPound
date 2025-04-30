"""MongoDB lifespan configuration for the FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from .database import client


@asynccontextmanager
async def mongo_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Handle MongoDB lifespan events.
    Sets up and tears down database connection.
    """
    try:
        yield
    finally:
        client.close()
