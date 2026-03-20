from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Annotated, Any, get_args, get_origin

from annotated_doc import Doc
from pydantic import BaseModel

if TYPE_CHECKING:
    from fasthttp.app import FastHTTP
    from fasthttp.routing import Route


def _get_type_string(annotation: Any) -> str | None:
    """Convert Python type annotation to OpenAPI type string."""
    if annotation is None:
        return {"type": "string", "nullable": True}

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Annotated:
        return _get_type_string(args[0])

    if origin is list:
        item_type = _get_type_string(args[0]) if args else None
        if item_type:
            return {"type": "array", "items": item_type}
        return {"type": "array"}

    if origin is dict:
        return {"type": "object"}

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    if annotation in type_map:
        return {"type": type_map[annotation]}

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return {"$ref": f"#/components/schemas/{annotation.__name__}"}

    return None


def _extract_docstring(func: Any) -> str:
    """Extract docstring from a function."""
    if func and hasattr(func, "__doc__") and func.__doc__:
        doc = inspect.getdoc(func)
        if doc:
            lines = [line.strip() for line in doc.strip().split("\n")]
            return " ".join(line for line in lines if line)
    return ""


def _generate_schema_from_model(model: type[BaseModel]) -> dict[str, Any]:
    """Generate OpenAPI schema from Pydantic model."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for name, field in model.model_fields.items():
        field_info = field.annotation

        description = None
        if field_info and get_origin(field_info) is Annotated:
            annotations = get_args(field_info)
            for ann in annotations:
                if isinstance(ann, Doc):
                    description = ann._doc

        type_schema = _get_type_string(field.annotation)
        if type_schema:
            prop_schema = type_schema.copy()
            if description:
                prop_schema["description"] = description
            if field.is_required():
                schema["required"].append(name)
            schema["properties"][name] = prop_schema
        else:
            schema["properties"][name] = {"type": "string"}

    if not schema["required"]:
        del schema["required"]

    return schema


def _generate_parameter_schema(params: dict | None) -> dict[str, Any]:
    """Generate OpenAPI parameter schema from params dict."""
    if not params:
        return {}

    properties = {}
    required = []

    for name, value in params.items():
        properties[name] = _get_type_string(type(value)) or {"type": "string"}
        required.append(name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _generate_response_schema(
    response_model: type[BaseModel] | None,
) -> dict[str, Any]:
    """Generate OpenAPI response schema from response model."""
    if not response_model:
        return {"description": "Successful response"}

    origin = get_origin(response_model)
    args = get_args(response_model)

    if origin is list and args:
        item_model = args[0]
        if isinstance(item_model, type) and issubclass(item_model, BaseModel):
            return {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"$ref": f"#/components/schemas/{item_model.__name__}"}
                        }
                    }
                },
            }
        else:
            return {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"type": "array"}
                    }
                },
            }

    try:
        if isinstance(response_model, type) and issubclass(response_model, BaseModel):
            return {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{response_model.__name__}"}
                    }
                },
            }
    except TypeError:
        pass

    return {"description": "Successful response"}


def _generate_error_response_schema(
    status_code: int,
    model: type[BaseModel] | None,
) -> dict[str, Any]:
    """Generate OpenAPI error response schema."""
    if not model:
        return {
            "description": f"Error response (HTTP {status_code})",
        }

    return {
        "description": f"Error response (HTTP {status_code})",
        "content": {
            "application/json": {
                "schema": {"$ref": f"#/components/schemas/{model.__name__}"}
            }
        },
    }


def _collect_schemas(routes: list[Route]) -> dict[str, Any]:
    """Collect all Pydantic schemas from routes."""
    schemas: dict[str, Any] = {}

    for route in routes:
        if route.response_model:
            model = route.response_model
            origin = get_origin(model)
            if origin is list:
                args = get_args(model)
                if args:
                    model = args[0]

            try:
                if isinstance(model, type) and issubclass(model, BaseModel):
                    if model.__name__ not in schemas:
                        schemas[model.__name__] = _generate_schema_from_model(model)
            except TypeError:
                pass

        if route.request_model:
            model = route.request_model
            try:
                if isinstance(model, type) and issubclass(model, BaseModel):
                    if model.__name__ not in schemas:
                        schemas[model.__name__] = _generate_schema_from_model(model)
            except TypeError:
                pass

        if route.responses:
            for status_code, response_config in route.responses.items():
                model = response_config.get("model")
                try:
                    if model and isinstance(model, type) and issubclass(model, BaseModel):
                        if model.__name__ not in schemas:
                            schemas[model.__name__] = _generate_schema_from_model(model)
                except TypeError:
                    pass

    return schemas


def _normalize_path(url: str) -> str:
    """
    Normalize URL to valid OpenAPI path.

    Converts full URLs like https://example.com/api/users
    to /example.com/api/users format.
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = parsed.netloc.replace(':', '_')
    path = parsed.path

    if not path:
        path = "/"

    api_path = f"/{host}{path}"

    if parsed.query:
        api_path = f"{api_path}?{parsed.query}"

    return api_path


def generate_openapi_schema(app: FastHTTP) -> dict[str, Any]:
    """
    Generate OpenAPI 3.0 schema from FastHTTP application.

    Args:
        app: FastHTTP application instance.

    Returns:
        OpenAPI schema as a dictionary.
    """
    routes = app.routes

    schemas = _collect_schemas(routes)

    paths: dict[str, Any] = {}

    for route in routes:
        path_item: dict[str, Any] = {}

        handler = route.handler
        if hasattr(handler, "__wrapped__"):
            handler = handler.__wrapped__

        summary = _extract_docstring(handler) or route.url

        operation: dict[str, Any] = {
            "summary": summary,
            "operationId": f"{route.method.lower()}_{route.url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '').replace('.', '_')}",
            "tags": route.tags or ["Default"],
            "responses": {},
            "x-original-url": route.url,
        }

        if handler and hasattr(handler, "__doc__") and handler.__doc__:
            operation["description"] = _extract_docstring(handler)

        if route.params:
            operation["parameters"] = [
                {
                    "name": name,
                    "in": "query",
                    "schema": _get_type_string(type(value)),
                    "required": True,
                }
                for name, value in route.params.items()
            ]

        if route.json or route.data or route.request_model:
            request_body: dict[str, Any] = {
                "required": True,
                "content": {},
            }

            if route.request_model:
                request_body["content"] = {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{route.request_model.__name__}"
                        }
                    }
                }
            elif route.json:
                request_body["content"] = {
                    "application/json": {
                        "schema": _get_type_string(type(route.json)) or {"type": "object"}
                    }
                }
            else:
                request_body["content"] = {
                    "text/plain": {
                        "schema": {"type": "string"}
                    }
                }

            operation["requestBody"] = request_body

        if route.response_model:
            operation["responses"]["200"] = _generate_response_schema(
                route.response_model
            )
        else:
            operation["responses"]["200"] = {
                "description": "Successful response",
            }

        if route.responses:
            for status_code, response_config in route.responses.items():
                model = response_config.get("model")
                operation["responses"][str(status_code)] = _generate_error_response_schema(
                    status_code, model
                )
        else:
            operation["responses"]["400"] = {"description": "Bad request"}
            operation["responses"]["500"] = {"description": "Internal server error"}

        method_lower = route.method.lower()
        path_item[method_lower] = operation

        path_key = _normalize_path(route.url)
        if path_key in paths:
            paths[path_key][method_lower] = operation
        else:
            paths[path_key] = path_item

    openapi_schema: dict[str, Any] = {
        "openapi": "3.0.3",
        "info": {
            "title": "FastHTTP API",
            "description": "HTTP Client API documentation",
            "version": "1.0.0",
        },
        "paths": paths,
        "components": {
            "schemas": schemas,
        },
    }

    return openapi_schema
