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
        method: Annotated[
            str | None,
            Doc(
                """
                HTTP method of the request.

                The HTTP method used to send the request
                (e.g. GET, POST, PUT, PATCH, DELETE).
                """
            ),
        ] = None,
        req_headers: Annotated[
            dict | None,
            Doc(
                """
                HTTP headers of the request.

                A mapping of header names to their values
                that were sent with the request.
                """
            ),
        ] = None,
        query: Annotated[
            dict | None,
            Doc(
                """
                Query parameters of the request.

                The dictionary of query parameters that were
                encoded into the URL query string.
                """
            ),
        ] = None,
        req_json: Annotated[
            dict | None,
            Doc(
                """
                JSON body of the request.

                The JSON data that was sent with the request,
                if the request had a JSON body.
                """
            ),
        ] = None,
        req_data: Annotated[
            object | None,
            Doc(
                """
                Raw data of the request.

                The raw data that was sent with the request,
                such as form data, plain text, or binary payload.
                """
            ),
        ] = None,
    ) -> None:
        self.status = status
        self.text = text
        self.headers = headers
        self._handler_result = None

        self._method = method
        self._req_headers = req_headers
        self._query = query
        self._req_json = req_json
        self._req_data = req_data

    @property
    def method(
        self,
    ) -> Annotated[
        str | None,
        Doc(
            """
            HTTP method of the request.

            Returns the HTTP method used to send the request
            (e.g. GET, POST, PUT, PATCH, DELETE).
            Returns None if the method is not available.
            """
        ),
    ]:
        return self._method

    @method.setter
    def method(self, value: str | None) -> None:
        self._method = value

    @property
    def req_headers(
        self,
    ) -> Annotated[
        dict | None,
        Doc(
            """
            HTTP headers of the request.

            Returns a dictionary of header names to their values
            that were sent with the request.
            Returns None if headers are not available.
            """
        ),
    ]:
        return self._req_headers

    @req_headers.setter
    def req_headers(self, value: dict | None) -> None:
        self._req_headers = value

    @property
    def query(
        self,
    ) -> Annotated[
        dict | None,
        Doc(
            """
            Query parameters of the request.

            Returns a dictionary of query parameters that were
            encoded into the URL query string.
            Returns None if no query parameters were provided.
            """
        ),
    ]:
        return self._query

    @query.setter
    def query(self, value: dict | None) -> None:
        self._query = value

    @property
    def path_params(
        self,
    ) -> Annotated[
        dict,
        Doc(
            """
            Path parameters of the request.

            Returns an empty dictionary as FastHTTP does not
            support path parameters in the traditional sense.
            This property is provided for compatibility with
            web frameworks that use path parameters.
            """
        ),
    ]:
        return {}

    def json(self) -> JSONResponse.Value:
        """
        Parse the response body as JSON.

        Returns the parsed JSON object. Raises a
        ValueError if the response body is not valid JSON.
        """
        return json.loads(self.text)

    def req_json(
        self,
    ) -> Annotated[
        dict | None,
        Doc(
            """
            JSON body of the request.

            Returns the JSON data that was sent with the request,
            if the request had a JSON body.
            Returns None if no JSON body was provided.
            """
        ),
    ]:
        return self._req_json

    def req_text(
        self,
    ) -> Annotated[
        str | None,
        Doc(
            """
            Text representation of the request body.

            Returns the request body as a string if available.
            For JSON requests, this returns the JSON string.
            For raw data requests, this returns the string
            representation of the data.
            Returns None if no body data is available.
            """
        ),
    ]:
        if self._req_json is not None:
            return json.dumps(self._req_json)
        if self._req_data is not None:
            return str(self._req_data)
        return None

    def __repr__(self) -> str:
        """
                Return a debug-friendly string representation
        of the response.
        """
        return f"<Response [{self.status}]>"
