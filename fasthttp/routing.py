from collections.abc import Callable
from typing import Annotated, Any, Literal

from annotated_doc import Doc


class Route:
    """
    Definition of an HTTP request route.

    A Route binds together an HTTP method, a target URL,
    optional request data, and a response handler function.

    It is used by FastHTTP to send requests and process
    responses in a structured and predictable way.
    """
    def __init__(
        self,
        *,
        method: Annotated[
            Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
            Doc(
                """
                HTTP method for the request.

                Determines how the request will be sent to the server.

                Suppoeted methods are:
                GET, POST, PUT, PATCH, DELETE.
                """
            )],
        url: Annotated[
            str,
            Doc(
                """
                Target URL for the HTTP request.

                Must be a full URL including scheme, host and path
                Example:
                https://api.google.com/
                """
            )],
        handler: Annotated[
            Callable,
            Doc(
                """
                Response handler function.

                This asyncfunction will be called with a Response object
                and can return:
                - str
                - Response
                - None
                """
            )],
        params: Annotated[
            dict | None,
            Doc(
                """
                Query parameters to be sent with the request.

                The dictionary will be encoded into the URL query string
                and appended to the request URL.
                """
            )] = None,
        json: Annotated[
            dict | None,
            Doc(
                """
                JSON body to be sent with the request.

                The data will be serialized to JSON and sent with the

                application/json Content-Type header.
                """
            )] = None,
        data: Annotated[
            Any | None,
            Doc(
                """

                Raw request body or form data.

                Can be used to send form-encoded data, plain text,

                binary payloads or any custom request body.
                """
            )] = None,
    ) -> None:
        self.method = method
        self.url = url
        self.handler = handler
        self.params = params
        self.json = json
        self.data = data
