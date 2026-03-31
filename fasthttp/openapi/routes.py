from __future__ import annotations

import json
from typing import TYPE_CHECKING, Annotated, Any

import httpx
from annotated_doc import Doc

from fasthttp.response import Response
from fasthttp import status
from .generator import generate_openapi_schema
from .swagger import get_swagger_html, get_not_found_html
from .urls import build_docs_urls

if TYPE_CHECKING:
    from fasthttp.app import FastHTTP


async def handle_docs(
    app: Annotated[
        "FastHTTP",
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
        "FastHTTP",
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
    json_str = json.dumps(schema, indent=2, ensure_ascii=False)
    return Response(
        status=status.HTTP_200_OK,
        text=json_str,
        headers={"Content-Type": "application/json"},
    )


async def handle_not_found(
    path: Annotated[
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
    ]
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
            text=json.dumps({"error": "URL is required"}),
            headers={"Content-Type": "application/json"},
        )

    try:
        async with httpx.AsyncClient() as client:
            kwargs: dict[str, Any] = {
                "method": method,
                "url": url,
                "headers": headers,
            }

            if body and method in ("POST", "PUT", "PATCH"):
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

            try:
                result["json"] = response.json()
            except Exception:
                pass

            return Response(
                status=status.HTTP_200_OK,
                text=json.dumps(result, indent=2, ensure_ascii=False),
                headers={"Content-Type": "application/json"},
            )

    except httpx.ConnectError as e:
        return Response(
            status=status.HTTP_502_BAD_GATEWAY,
            text=json.dumps({"error": f"Connection error: {str(e)}"}),
            headers={"Content-Type": "application/json"},
        )
    except httpx.TimeoutException as e:
        return Response(
            status=status.HTTP_504_GATEWAY_TIMEOUT,
            text=json.dumps({"error": f"Timeout: {str(e)}"}),
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            text=json.dumps({"error": f"Request failed: {str(e)}"}),
            headers={"Content-Type": "application/json"},
        )
