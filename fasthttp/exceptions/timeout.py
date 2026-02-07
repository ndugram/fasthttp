from typing import Annotated

from annotated_doc import Doc

from .base import FastHTTPError


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
        message: (
            Annotated[
                str,
                Doc(
                    """
                Optional custom error message.

                If not provided, a default
                "Request timed out" message is used.
                """
                ),
            ]
            | None
        ) = None,
        url: (
            Annotated[
                str,
                Doc(
                    """
                Request URL that exceeded the timeout limit.
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
                HTTP method used for the timed-out request.
                """
                ),
            ]
            | None
        ) = None,
        timeout: (
            Annotated[
                int,
                Doc(
                    """
                Timeout value in seconds that was exceeded.

                Stored in the error details for
                debugging and logging purposes.
                """
                ),
            ]
            | None
        ) = None,
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
