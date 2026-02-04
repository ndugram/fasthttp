from __future__ import annotations

import logging
from typing import Annotated, Any

from annotated_doc import Doc

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
            )],
        url: Annotated[
            str,
            Doc(
                """
                Request URL associated with the error.

                Contains the full URL of the HTTP request
                that caused this exception, if available.
                """
            )] | None = None,
        method: Annotated[
            str,
            Doc(
                """
                HTTP method of the failed request.

                Examples: GET, POST, PUT, PATCH, DELETE.
                """
            )] | None = None,
        status_code: Annotated[
            int,
            Doc(
                """
                HTTP response status code.

                Represents the server response code
                (e.g. 404, 500). May be None if the request
                failed before receiving a response.
                """
            )] | None = None,
        details: Annotated[
            dict[str, Any],
            Doc(
                """
                Additional error details.

                Arbitrary dictionary with extra diagnostic
                information such as response body, headers,
                exception metadata or debug context.
                """
            )] | None = None,
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
            details_str = ", ".join(
                f"{k}={v}" for k, v in self.details.items()
                )
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


class FastHTTPConnectionError(FastHTTPError):
    """
    Raised when connection to the server fails.

    Example:
        >>> raise FastHTTPConnectionError
        (
            "Failed to connect",
            url="https://httpbin.org/get"
        )
    """

    def __init__(
        self,
        message: Annotated[
            str,
            Doc(
                """
                Human-readable error message.

                Describes the reason why the connection to the server failed.
                This message is intended to be shown to the user or logged.
                """
            )] = "Connection failed",
        url: Annotated[
            str,
            Doc(
                """
                Request URL that the client failed to connect to.

                Contains the full target URL including scheme, host and path.
                Useful for debugging connection issues.
                """
            )] | None = None,
        method: Annotated[
            str,
            Doc(
                """
                HTTP method used for the failed request.

                Examples: GET, POST, PUT, PATCH, DELETE.
                Helps identify which type of request caused the error.
                """
            )] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            message=message,
            url=url,
            method=method,
            **kwargs,
        )


class FastHTTPTimeoutError(FastHTTPError):
    """
    Raised when request exceeds timeout limit.

    Example:
        >>> raise FastHTTPTimeoutError
        (
            "Request timed out",
            url="https://httpbin.org/delay/10",
            timeout=5
        )
    """

    def __init__(
        self,
        message: Annotated[
            str,
            Doc(
                """
                Optional custom error message.

                If not provided, a default
                "Request timed out" message is used.
                """
            )] | None = None,
        url: Annotated[
            str,
            Doc(
                """
                Request URL that exceeded the timeout limit.
                """
            )] | None = None,
        method: Annotated[
            str,
            Doc(
                """
                HTTP method used for the timed-out request.
                """
            )] | None = None,
        timeout: Annotated[
            int,
            Doc(
                """
                Timeout value in seconds that was exceeded.

                Stored in the error details for
                debugging and logging purposes.
                """
            )] | None = None,
        **kwargs,
    ) -> None:
        timeout_msg = message or "Request timed out"
        details = {"timeout": timeout} if timeout else {}
        details.update(kwargs.pop("details", {}) or {})

        super().__init__(
            message=timeout_msg,
            url=url,
            method=method,
            details=details,
            **kwargs,
        )


class FastHTTPBadStatusError(FastHTTPError):
    """
    Raised when server returns an error status code (4xx, 5xx).

    Example:
        >>> raise FastHTTPBadStatusError
        (
            "404 Not Found",
            url="https://httpbin.org/status/404",
            status_code=404
        )
    """

    def __init__(
        self,
        message: Annotated[
            str,
            Doc(
                """
                Optional custom error message.

                If not provided, a message will be generated
                based on the HTTP status code (e.g. "HTTP 404").

                The message may be colorized depending on
                the status severity.
                """
            )] | None = None,
        url: Annotated[
            str,
            Doc(
                """
                Request URL that returned an error status code.
                """
            )] | None = None,
        method: Annotated[
            str,
            Doc(
                """
                HTTP method used for the failed request.
                """
            )] | None = None,
        status_code: Annotated[
            int,
            Doc(
                """
                HTTP response status code returned by the server.

                Typically a client error (4xx)
                or server error (5xx).
                """
            )] | None = None,
        response_body: Annotated[
            str,
            Doc(
                """
                Raw response body returned by the server.

                If provided, a short preview of the body
                will be stored in the error details
                for debugging purposes.
                """
            )] | None = None,
        **kwargs,
    ) -> None:
        status_msg = message or (
            f"HTTP {status_code}" if status_code else "Bad status"
            )

        # Status message colorization is handled by logging.py

        details = {}
        if response_body:
            details["body_preview"] = response_body[:100] + "..." if len(response_body) > 100 else response_body
        details.update(kwargs.pop("details", {}) or {})

        super().__init__(
            message=status_msg,
            url=url,
            method=method,
            status_code=status_code,
            details=details,
            **kwargs,
        )


class FastHTTPRequestError(FastHTTPError):
    """
    Raised when request preparation or execution fails.

    Example:
        >>> raise FastHTTPRequestError
        (
            "Invalid URL",
            url="invalid-url"
        )
    """

    def __init__(
        self,
        message: Annotated[
            str,
            Doc(
                """
                Description of the request-level error.

                Used when request preparation or execution
                fails before receiving a response
                (e.g. invalid URL, invalid parameters).
                """
            )],
        url: Annotated[
            str,
            Doc(
                """
                Target request URL that caused the error.

                May be invalid, malformed or unsupported.
                """
            )] | None = None,
        method: Annotated[
            str,
            Doc(
                """
                HTTP method that was being used

                when the request error occurred.
                """
            )] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            message=message,
            url=url,
            method=method,
            **kwargs,
        )


class FastHTTPValidationError(FastHTTPError):
    """
    Raised when request validation fails.

    Example:
        >>> raise FastHTTPValidationError
        (
            "Missing required field",
            details={"field": "email"}
        )
    """

    def __init__(
        self,
        message: Annotated[
            str,
            Doc(
                """
                Validation error description.

                Used when request configuration, parameters
                or payload fail validation checks.

                Examples include missing required fields,
                invalid data types or malformed input.
                """
            )] = "Validation failed",
        **kwargs,
    ) -> None:
        super().__init__(
            message=message,
            details=kwargs.pop("details", {}),
            **kwargs,
        )


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
    logger.info(
        f"✔ {method} {url} {status_code} {duration:.2f}s"
    )


