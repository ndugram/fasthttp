from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import FastHTTPError

logger = logging.getLogger("fasthttp.exceptions")

COLORS = {
    "red": "\033[91m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def colorize(text: str, color: str) -> str:
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def handle_error(error: FastHTTPError, raise_it: bool = True) -> None:
    """
    Handle a FastHTTP error with logging.

    Args:
        error: The exception to handle
        raise_it: Whether to re-raise the exception
    """
    error.log()
    if raise_it:
        raise error


def log_success(
    url: str,
    method: str,
    status_code: int,
    duration: float,
) -> None:
    logger.info("✔ %s %s %s %.2fs", method, url, status_code, duration)
