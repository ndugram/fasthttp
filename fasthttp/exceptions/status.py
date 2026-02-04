from typing import Annotated

from annotated_doc import Doc

from .base import FastHTTPError


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

