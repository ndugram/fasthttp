from typing import Annotated

from annotated_doc import Doc

from .base import FastHTTPError


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
