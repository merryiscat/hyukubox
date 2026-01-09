"""Logging configuration for MCP server.

⚠️ CRITICAL: Never log to stdout in STDIO mode - it breaks JSON-RPC!
Always use stderr or file logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Configure logging for MCP server.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging. If None, logs to stderr only.

    Returns:
        Configured logger instance

    Warning:
        NEVER log to stdout in STDIO mode - it corrupts JSON-RPC messages!
    """
    # Create logger
    logger = logging.getLogger("hyukebox")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Prevent propagation to avoid double logging
    logger.propagate = False

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # STDERR handler (safe for STDIO transport)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # Optional file handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger


# Global logger instance
logger = setup_logging()
