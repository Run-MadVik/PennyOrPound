"""
This is the entry point for the application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.router import router as v1_router
from .config import logger, mongo_lifespan  # noqa

app = FastAPI(
    title="PennyOrPound",
    description="An expense tracker",
    version="1.0.0",
    lifespan=mongo_lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1_router)
