from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Annotated, Any

import httpx
import orjson
from annotated_doc import Doc

from fasthttp import status
from fasthttp.response import Response

from .generator import generate_openapi_schema
from .swagger import get_not_found_html, get_swagger_html
from .urls import build_docs_urls

if TYPE_CHECKING:
    from fasthttp.app import FastHTTP


async def handle_docs(
    _app: Annotated[
        FastHTTP,
        Doc("FastHTTP application instance"),
    ],
    base_url: Annotated[
        str,
        Doc("Optional docs base URL prefix"),
    ] = "",
) -> Response:
    """
    Serve Swagger UI HTML.

    Returns:
        Response with Swagger UI HTML.
    """
    urls = build_docs_urls(base_url)
    html = get_swagger_html(
        openapi_url=urls["openapi_url"],
        request_url=urls["request_url"],
    )
    return Response(
        status=status.HTTP_200_OK,
        text=html,
        headers={"Content-Type": "text/html"},
    )


async def handle_openapi_json(
    app: Annotated[
        FastHTTP,
        Doc("FastHTTP application instance"),
    ],
    base_url: Annotated[
        str,
        Doc("Optional docs base URL prefix"),
    ] = "",
) -> Response:
    """
    Serve OpenAPI schema as JSON.

    Returns:
        Response with OpenAPI JSON schema.
    """
    urls = build_docs_urls(base_url)
    schema = generate_openapi_schema(app, server_url=urls["request_url"])
    json_str = orjson.dumps(schema, option=orjson.OPT_INDENT_2).decode()
    return Response(
        status=status.HTTP_200_OK,
        text=json_str,
        headers={"Content-Type": "application/json"},
    )


async def handle_not_found(
    _path: Annotated[
        str,
        Doc("The requested path that was not found"),
    ],
    base_url: Annotated[
        str,
        Doc("Optional docs base URL prefix"),
    ] = "",
) -> Response:
    """
    Serve custom 404 page for unknown routes.

    Returns:
        Response with stylish 404 page.
    """
    urls = build_docs_urls(base_url)
    html = get_not_found_html(
        docs_url=urls["docs_url"],
        openapi_url=urls["openapi_url"],
        redoc_url=urls["redoc_url"],
    )
    return Response(
        status=status.HTTP_404_NOT_FOUND,
        text=html,
        headers={"Content-Type": "text/html"},
    )


async def handle_request(
    request_data: Annotated[
        dict[str, Any],
        Doc("Request data from Swagger UI"),
    ],
) -> Response:
    """
    Execute HTTP request and return results for Swagger UI.

    This endpoint receives request details from Swagger UI
    and executes the actual HTTP request using httpx.

    Args:
        request_data: Dictionary with:
            - method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            - url: Target URL
            - headers: Request headers (optional)
            - body: Request body for POST/PUT/PATCH (optional)

    Returns:
        Response with status, headers, and body.
    """
    method = request_data.get("method", "GET")
    url = request_data.get("url", "")
    headers = request_data.get("headers", {})
    body = request_data.get("body")

    if not url:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            text=orjson.dumps({"error": "URL is required"}).decode(),
            headers={"Content-Type": "application/json"},
        )

    try:
        async with httpx.AsyncClient() as client:
            kwargs: dict[str, Any] = {
                "method": method,
                "url": url,
                "headers": headers,
            }

            if body and method in ("POST", "PUT", "PATCH", "QUERY"):
                if isinstance(body, dict):
                    kwargs["json"] = body
                else:
                    kwargs["content"] = str(body)

            response = await client.request(**kwargs)

            result = {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
            }

            with contextlib.suppress(Exception):
                result["json"] = response.json()

            return Response(
                status=status.HTTP_200_OK,
                text=orjson.dumps(result, option=orjson.OPT_INDENT_2).decode(),
                headers={"Content-Type": "application/json"},
            )

    except httpx.ConnectError as e:
        return Response(
            status=status.HTTP_502_BAD_GATEWAY,
            text=orjson.dumps({"error": f"Connection error: {e!s}"}).decode(),
            headers={"Content-Type": "application/json"},
        )
    except httpx.TimeoutException as e:
        return Response(
            status=status.HTTP_504_GATEWAY_TIMEOUT,
            text=orjson.dumps({"error": f"Timeout: {e!s}"}).decode(),
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:  # noqa: BLE001
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            text=orjson.dumps({"error": f"Request failed: {e!s}"}).decode(),
            headers={"Content-Type": "application/json"},
        )
