"""Logging configuration for the application."""

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


# Configure logging
def setup_logger(name: str = "pennyorpound") -> logging.Logger:
    """Set up logger with both file and console handlers."""
    log_instance = logging.getLogger(name)
    log_instance.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if log_instance.handlers:
        return log_instance

    # Format for logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)

    # File Handler (Rotating file handler to manage log size)
    file_handler = RotatingFileHandler(
        logs_dir / os.environ.get("LOG_FILE", "app.log"),
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    log_instance.addHandler(console_handler)
    log_instance.addHandler(file_handler)

    return log_instance


# Create default logger instance
logger = setup_logger()
