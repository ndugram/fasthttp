from typing import Annotated

from annotated_doc import Doc

from .base import FastHTTPError


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
            ),
        ] = "Validation failed",
        **kwargs,
    ) -> None:
        super().__init__(
            message=message,
            details=kwargs.pop("details", {}),
            **kwargs,
        )
