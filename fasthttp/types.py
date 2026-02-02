from typing import Annotated, TypeAlias, TypedDict

from annotated_doc import Doc


class JSONResponse:
    """
    JSON response type definitions.

    This class groups type aliases that describe valid JSON data
    structures returned by HTTP responses.

    It is used for type-safe annotations of parsed JSON payloads,
    including primitive values, lists, and nested objects.
    """
    Primutive: TypeAlias = str | int | float | bool | None
    Value: TypeAlias = Primutive | list["Value"] | dict[str, "Value"]


class RequestsOptinal(TypedDict, total=False):
    """
    Optional request configuration.

    Defines optional parameters that control how HTTP requests
    are sent, such as headers, timeouts, and redirect behavior.

    All fields are optional and may be omitted if not needed.
    """
    headers: Annotated[
        dict[str, str],
        Doc(
            """
            HTTP headers to be sent with the request.
            A dictionary of header names and values that will be included
            in every request of this method type.
            """
        )]
    timeout: Annotated[
        float,
        Doc(
            """
            Request timeout in seconds.
            Specifies the maximum amount of time to wait for the server
            to respond before the request is cancelled.
            """
        )]
    allow_redirects: Annotated[
        bool,
        Doc(
            """
            Enable or disable HTTP redirects.
            When set to True, the client will automatically follow
            redirect responses (3xx status codes).
            """
        )]
