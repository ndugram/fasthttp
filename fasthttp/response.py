import json
from typing import Annotated

from annotated_doc import Doc

from .types import JSONResponse


class Response:
    """
    HTTP response object.

    Represents an HTTP response returned by the server,
    including status code, raw body text, and response headers.

    Used by FastHTTP to pass response data to route handlers.
    """

    def __init__(
        self,
        status: Annotated[
            int,
            Doc(
                """
                HTTP status code of the response.

                Indicates the result of the HTTP request
                (e.g. 200 for success, 404 for not found,
                500 for server error).
                """
            ),
        ],
        text: Annotated[
            str,
            Doc(
                """
                Raw response body as a string.

                Contains the response payload exactly as
                returned by the server.
                """
            ),
        ],
        headers: Annotated[
            dict,
            Doc(
                """
                HTTP response headers.

                A mapping of header names to their values
                returned by the server.
                """
            ),
        ],
    ) -> None:
        self.status = status
        self.text = text
        self.headers = headers
        self._handler_result = None

    def json(self) -> JSONResponse.Value:
        """
        Parse the response body as JSON.

        Returns the parsed JSON object. Raises a
        ValueError if the response body is not valid JSON.
        """
        return json.loads(self.text)

    def __repr__(self) -> str:
        """
                Return a debug-friendly string representation
        of the response.
        """
        return f"<Response [{self.status}]>"
