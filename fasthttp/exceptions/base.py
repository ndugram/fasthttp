from __future__ import annotations

import logging
from typing import Annotated, Any

from annotated_doc import Doc

logger = logging.getLogger("fasthttp.exceptions")


class FastHTTPError(Exception):
    """
    Base exception for FastHTTP library.

    Attributes:
        message: Error description
        url: Request URL
        method: HTTP method
        status_code: Response status code
    """

    def __init__(
        self,
        message: Annotated[
            str,
            Doc(
                """
                Human-readable error message.

                Describes what went wrong during request
                execution or response handling.
                """
            ),
        ],
        url: (
            Annotated[
                str,
                Doc(
                    """
                Request URL associated with the error.

                Contains the full URL of the HTTP request
                that caused this exception, if available.
                """
                ),
            ]
            | None
        ) = None,
        method: (
            Annotated[
                str,
                Doc(
                    """
                HTTP method of the failed request.

                Examples: GET, POST, PUT, PATCH, DELETE.
                """
                ),
            ]
            | None
        ) = None,
        status_code: (
            Annotated[
                int,
                Doc(
                    """
                HTTP response status code.

                Represents the server response code
                (e.g. 404, 500). May be None if the request
                failed before receiving a response.
                """
                ),
            ]
            | None
        ) = None,
        details: (
            Annotated[
                dict[str, Any],
                Doc(
                    """
                Additional error details.

                Arbitrary dictionary with extra diagnostic
                information such as response body, headers,
                exception metadata or debug context.
                """
                ),
            ]
            | None
        ) = None,
    ) -> None:
        self.message = message
        self.url = url
        self.method = method
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        parts = [self.message]

        if self.url:
            parts.append(f"URL: {self.url}")
        if self.method:
            parts.append(f"Method: {self.method}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")

        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            parts.append(f"Details: {details_str}")

        return " | ".join(parts)

    def log(self, level: int = logging.ERROR) -> None:
        log_message = f"{self.__class__.__name__}: {self.message}"

        if self.url:
            log_message += f" | URL: {self.url}"
        if self.method:
            log_message += f" | Method: {self.method}"
        if self.status_code:
            log_message += f" | Status: {self.status_code}"

        logger.log(level, log_message)
