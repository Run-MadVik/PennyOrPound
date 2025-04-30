"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": FastAPI().version,
        }
    )
