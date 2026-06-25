"""
Centralized logging for Smart Admin Assistant.
Usage:
    from app.logger import get_logger
    logger = get_logger(__name__)
    logger.info("System started")
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, log_file: str = None, level: str = "INFO") -> logging.Logger:
    """
    Create and return a configured logger.

    Args:
        name: Logger name (usually __name__).
        log_file: Optional path to a log file for persistent logging.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # ─── Formatter ───────────────────────────────────────────
    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(name)-25s │ %(levelname)-8s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ─── Console Handler ────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ─── File Handler (optional) ────────────────────────────
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
