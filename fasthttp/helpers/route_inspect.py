from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Callable



# Route params type for HTTP methods
RouteParams = dict[str, Any]


def check_annotated_parameters(*, func: Callable[..., object]) -> None:
    """
    Validate that all function parameters have type annotations.

    Args:
        func: Target function to validate.

    Raises:
        TypeError: If any parameter does not have a type annotation.
    """
    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        if param.annotation is inspect.Parameter.empty:
            msg = (
                f"Parameter '{name}' in function '{func.__name__}' "
                "must have a type annotation"
            )
            raise TypeError(msg)


def check_annotated_return(*, func: Callable[..., object]) -> None:
    """
    Validate that a function has an explicit return type annotation.

    Args:
        func: Target function to validate.

    Raises:
        TypeError: If the function does not have a return type annotation.
    """
    sig = inspect.signature(func)
    if sig.return_annotation is inspect.Signature.empty:
        msg = (
            f"Function '{func.__name__}' must explicitly "
            "define return type annotation"
        )
        raise TypeError(msg)


def validate_handler(func: Callable[..., object]) -> None:
    """
    Validate a handler function has proper type annotations.

    Checks both parameters and return type annotations.

    Args:
        func: Handler function to validate.

    Raises:
        TypeError: If validation fails.
    """
    check_annotated_parameters(func=func)
    check_annotated_return(func=func)


# Common parameters for HTTP methods
COMMON_PARAMS = {
    "response_model": {
        "type": type[BaseModel] | None,
        "default": None,
        "doc": "Optional Pydantic model for validating the handler result.",
    },
    "request_model": {
        "type": type[BaseModel] | None,
        "default": None,
        "doc": "Optional Pydantic model for validating request data.",
    },
    "tags": {
        "type": list[str] | None,
        "default": None,
        "doc": "Optional tags for grouping and filtering the route.",
    },
    "dependencies": {
        "type": list | None,
        "default": None,
        "doc": "Optional dependencies executed before the request.",
    },
    "responses": {
        "type": dict[int, dict[Literal["model"], type[BaseModel]]] | None,
        "default": None,
        "doc": "Optional response models for error status codes.",
    },
}


def create_route_params(
    *,
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
    url: str,
    params: dict | None = None,
    json: dict | None = None,
    data: object | None = None,
    response_model: type[BaseModel] | None = None,
    request_model: type[BaseModel] | None = None,
    tags: list[str] | None = None,
    dependencies: list | None = None,
    skip_request: bool = False,
    responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
) -> RouteParams:
    """
    Create a route parameters dictionary from common arguments.

    Args:
        method: HTTP method.
        url: Target URL.
        params: Query parameters.
        json: JSON body.
        data: Raw body.
        response_model: Response model.
        request_model: Request model.
        tags: Route tags.
        dependencies: Route dependencies.
        skip_request: Skip HTTP request flag.
        responses: Response models for status codes.

    Returns:
        Dictionary of route parameters.
    """
    return {
        "method": method,
        "url": url,
        "params": params,
        "json": json,
        "data": data,
        "response_model": response_model,
        "request_model": request_model,
        "tags": tags or [],
        "dependencies": dependencies or [],
        "skip_request": skip_request,
        "responses": responses or {},
    }


__all__ = (
    "COMMON_PARAMS",
    "check_annotated_parameters",
    "check_annotated_return",
    "create_route_params",
    "validate_handler",
)
