"""
Centralized logging configuration for StockSense application.
Provides consistent logging across all modules with both file and console output.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from constants import (
    LOG_LEVEL,
    LOG_FILE,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
)


def setup_logging() -> logging.Logger:
    """
    Configure and return the root logger for the application.

    Sets up both file and console handlers with appropriate formatting.
    Creates log file if it doesn't exist.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if needed
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file_path = log_dir / LOG_FILE

    # Configure root logger
    logger = logging.getLogger("stocksense")
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logging.warning(f"Could not create file handler: {e}")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name (str): Module name (typically __name__)

    Returns:
        logging.Logger: Logger instance for the module
    """
    return logging.getLogger(f"stocksense.{name}")


# Initialize logger at module load time
logger = setup_logging()
