from typing import Annotated

from annotated_doc import Doc

from .base import FastHTTPError


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
            ),
        ],
        url: (
            Annotated[
                str,
                Doc(
                    """
                Target request URL that caused the error.

                May be invalid, malformed or unsupported.
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
                HTTP method that was being used

                when the request error occurred.
                """
                ),
            ]
            | None
        ) = None,
        **kwargs,
    ) -> None:
        super().__init__(
            message=message,
            url=url,
            method=method,
            **kwargs,
        )
