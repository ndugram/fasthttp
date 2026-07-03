from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Annotated, Any, get_args, get_origin
from urllib.parse import urlparse

from annotated_doc import Doc
from pydantic import BaseModel, TypeAdapter
from pydantic.fields import FieldInfo
from pydantic.json_schema import models_json_schema

from fasthttp.auth import BasicAuth, BearerAuth, DigestAuth, OAuth2ClientCredentials

if TYPE_CHECKING:
    from fasthttp.app import FastHTTP
    from fasthttp.routing import Route

REF_TEMPLATE = "#/components/schemas/{model}"
_EXAMPLE_TYPES = (str, int, float, bool)


def _extract_docstring(func: Any) -> str:  # noqa: ANN401
    """Extract docstring from a function."""
    if func and hasattr(func, "__doc__") and func.__doc__:
        doc = inspect.getdoc(func)
        if doc:
            lines = [line.strip() for line in doc.strip().split("\n")]
            return " ".join(line for line in lines if line)
    return ""


def _iter_field_models(annotation: Any) -> list[type[BaseModel]]:  # noqa: ANN401
    """Recursively find Pydantic models reachable through a type annotation."""
    origin = get_origin(annotation)

    if origin is Annotated:
        return _iter_field_models(get_args(annotation)[0])

    if origin is not None:
        models: list[type[BaseModel]] = []
        for arg in get_args(annotation):
            models.extend(_iter_field_models(arg))
        return models

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [annotation]

    return []


def _collect_model_closure(
    model: type[BaseModel], seen: set[type[BaseModel]]
) -> None:
    """Walk a model's fields to find every nested Pydantic model it references."""
    if model in seen:
        return
    seen.add(model)
    for field in model.model_fields.values():
        for nested in _iter_field_models(field.annotation):
            _collect_model_closure(nested, seen)


def _doc_description(field: FieldInfo) -> str | None:
    """Read a `Doc(...)` annotation from field metadata (annotated-doc convention)."""
    for meta in field.metadata:
        if isinstance(meta, Doc):
            return meta.documentation
    return None


class _SchemaCollector:
    """
    Builds `components/schemas` using Pydantic's own JSON Schema
    generation instead of a hand-written type mapper — this gives
    correct handling of enums, unions, constraints, defaults, and
    nested models for free.
    """

    def __init__(self, top_level_models: set[type[BaseModel]]) -> None:
        self.schemas: dict[str, Any] = {}
        self._refs: dict[type[BaseModel], dict[str, Any]] = {}

        closure: set[type[BaseModel]] = set()
        for model in top_level_models:
            _collect_model_closure(model, closure)

        if closure:
            key_map, top = models_json_schema(
                [(model, "serialization") for model in closure],
                ref_template=REF_TEMPLATE,
            )
            self.schemas.update(top.get("$defs", {}))
            for (model, _mode), ref in key_map.items():
                self._refs[model] = ref
            self._backfill_doc_descriptions(closure)

    def _backfill_doc_descriptions(self, models: set[type[BaseModel]]) -> None:
        """Fill in descriptions from `Doc(...)` metadata where Pydantic found none."""
        for model in models:
            schema = self.schemas.get(model.__name__)
            if not schema:
                continue
            properties = schema.get("properties", {})
            for name, field in model.model_fields.items():
                prop = properties.get(name)
                if prop is None or "description" in prop:
                    continue
                doc = _doc_description(field)
                if doc:
                    prop["description"] = doc

    def ref_for_model(self, model: type[BaseModel]) -> dict[str, Any]:
        """Return (and lazily register) a `$ref` for a model outside the original closure."""
        if model not in self._refs:
            closure: set[type[BaseModel]] = set()
            _collect_model_closure(model, closure)
            key_map, top = models_json_schema(
                [(m, "serialization") for m in closure],
                ref_template=REF_TEMPLATE,
            )
            self.schemas.update(top.get("$defs", {}))
            for (m, _mode), ref in key_map.items():
                self._refs[m] = ref
            self._backfill_doc_descriptions(closure)
        return self._refs[model]

    def schema_for_type(self, annotation: Any) -> dict[str, Any]:  # noqa: ANN401
        """Return an OpenAPI schema for an arbitrary Python type via `TypeAdapter`."""
        try:
            adapter = TypeAdapter(annotation)
            schema = adapter.json_schema(ref_template=REF_TEMPLATE)
        except Exception:  # noqa: BLE001
            return {"type": "object"}
        defs = schema.pop("$defs", None) or {}
        for name, def_schema in defs.items():
            self.schemas.setdefault(name, def_schema)
        return schema

    def schema_for_value(self, value: Any) -> dict[str, Any]:  # noqa: ANN401
        """Infer a best-effort schema from a concrete runtime value (query params, raw bodies)."""
        if isinstance(value, BaseModel):
            return self.ref_for_model(type(value))
        if isinstance(value, dict):
            return {
                "type": "object",
                "properties": {k: self.schema_for_value(v) for k, v in value.items()},
            }
        if isinstance(value, (list, tuple)):
            if value:
                return {"type": "array", "items": self.schema_for_value(value[0])}
            return {"type": "array"}
        return self.schema_for_type(type(value))

    def response_schema(self, model: type | None) -> dict[str, Any]:
        """Build a `responses.200`-style schema for a route's `response_model`."""
        if model is None:
            return {"description": "Successful response"}

        origin = get_origin(model)
        if origin is list:
            args = get_args(model)
            item = args[0] if args else None
            if isinstance(item, type) and issubclass(item, BaseModel):
                item_schema = self.ref_for_model(item)
            elif item is not None:
                item_schema = self.schema_for_type(item)
            else:
                item_schema = {}
            return {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"type": "array", "items": item_schema}
                    }
                },
            }

        if isinstance(model, type) and issubclass(model, BaseModel):
            return {
                "description": "Successful response",
                "content": {
                    "application/json": {"schema": self.ref_for_model(model)}
                },
            }

        return {
            "description": "Successful response",
            "content": {"application/json": {"schema": self.schema_for_type(model)}},
        }

    def error_response_schema(
        self, status_code: int, model: type[BaseModel] | None
    ) -> dict[str, Any]:
        """Build an error response schema (e.g. for `responses={404: {"model": ...}}`)."""
        if not model:
            return {"description": f"Error response (HTTP {status_code})"}
        return {
            "description": f"Error response (HTTP {status_code})",
            "content": {
                "application/json": {"schema": self.ref_for_model(model)}
            },
        }


def _normalize_path(url: str) -> str:
    """
    Normalize URL to valid OpenAPI path.

    Converts full URLs like https://example.com/api/users
    to /example.com/api/users format.
    """
    parsed = urlparse(url)
    host = parsed.netloc.replace(":", "_")
    path = parsed.path

    if not path:
        path = "/"

    api_path = f"/{host}{path}"

    if parsed.query:
        api_path = f"{api_path}?{parsed.query}"

    return api_path


def _get_security_scheme_name(
    auth: BasicAuth | BearerAuth | DigestAuth | OAuth2ClientCredentials,
) -> str:
    """Return the securityScheme key for a given auth object."""
    if isinstance(auth, BearerAuth):
        return "bearerAuth"
    if isinstance(auth, BasicAuth):
        return "basicAuth"
    if isinstance(auth, DigestAuth):
        return "digestAuth"
    if isinstance(auth, OAuth2ClientCredentials):
        return "oauth2ClientCredentials"
    return "auth"


def _collect_security_schemes(routes: list[Route]) -> dict[str, Any]:
    """Build components/securitySchemes from auth objects used in routes."""
    schemes: dict[str, Any] = {}

    for route in routes:
        if route.auth is None:
            continue
        if isinstance(route.auth, BearerAuth) and "bearerAuth" not in schemes:
            schemes["bearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        elif isinstance(route.auth, BasicAuth) and "basicAuth" not in schemes:
            schemes["basicAuth"] = {"type": "http", "scheme": "basic"}
        elif isinstance(route.auth, DigestAuth) and "digestAuth" not in schemes:
            schemes["digestAuth"] = {"type": "http", "scheme": "digest"}
        elif (
            isinstance(route.auth, OAuth2ClientCredentials)
            and "oauth2ClientCredentials" not in schemes
        ):
            schemes["oauth2ClientCredentials"] = {
                "type": "oauth2",
                "flows": {
                    "clientCredentials": {
                        "tokenUrl": route.auth.token_url,
                        "scopes": {s: "" for s in route.auth.scopes}
                        if route.auth.scopes
                        else {},
                    }
                },
            }

    return schemes


def _route_models(route: Route) -> list[type[BaseModel]]:
    """Every Pydantic model directly referenced by a route (unwrapped from list[...])."""
    models: list[type[BaseModel]] = []

    if route.response_model:
        model = route.response_model
        if get_origin(model) is list:
            args = get_args(model)
            model = args[0] if args else None
        if isinstance(model, type) and issubclass(model, BaseModel):
            models.append(model)

    if route.request_model:
        models.append(route.request_model)

    for response_config in (route.responses or {}).values():
        model = response_config.get("model")
        if isinstance(model, type) and issubclass(model, BaseModel):
            models.append(model)

    return models


def generate_openapi_schema(  # noqa: C901
    app: Annotated[
        FastHTTP,
        Doc("FastHTTP application instance."),
    ],
    *,
    server_url: Annotated[
        str | None,
        Doc(
            """
            Optional Swagger proxy server URL.

            When provided, it will be added to the OpenAPI `servers`
            section so Swagger UI can send requests through the
            FastHTTP proxy endpoint.
            """
        ),
    ] = None,
    title: Annotated[
        str,
        Doc("API title shown in the OpenAPI schema and Swagger UI."),
    ] = "FastHTTP API",
    version: Annotated[
        str,
        Doc("API version string."),
    ] = "1.0.0",
    description: Annotated[
        str,
        Doc("API description. Supports Markdown."),
    ] = "",
) -> dict[str, Any]:
    """
    Generate OpenAPI 3.0 schema from FastHTTP application.

    Args:
        app: FastHTTP application instance.
        server_url: Optional proxy URL added to the `servers` section.

    Returns:
        OpenAPI schema as a dictionary.
    """
    routes = app.routes

    top_level_models: set[type[BaseModel]] = set()
    for route in routes:
        top_level_models.update(_route_models(route))

    collector = _SchemaCollector(top_level_models)
    security_schemes = _collect_security_schemes(routes)

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
            "tags": route.tags or [urlparse(route.url).netloc or "default"],
            "responses": {},
            "x-original-url": route.url,
        }

        if handler and hasattr(handler, "__doc__") and handler.__doc__:
            operation["description"] = _extract_docstring(handler)

        if route.auth is not None:
            scheme_name = _get_security_scheme_name(route.auth)
            operation["security"] = [{scheme_name: []}]

        if route.params:
            parameters = []
            for name, value in route.params.items():
                param: dict[str, Any] = {
                    "name": name,
                    "in": "query",
                    "required": True,
                    "schema": collector.schema_for_value(value),
                }
                if isinstance(value, _EXAMPLE_TYPES):
                    param["example"] = value
                parameters.append(param)
            operation["parameters"] = parameters

        if route.json or route.data or route.request_model:
            request_body: dict[str, Any] = {"required": True, "content": {}}

            if route.request_model:
                request_body["content"] = {
                    "application/json": {
                        "schema": collector.ref_for_model(route.request_model)
                    }
                }
            elif route.json:
                request_body["content"] = {
                    "application/json": {
                        "schema": collector.schema_for_value(route.json),
                        "example": route.json,
                    }
                }
            else:
                content: dict[str, Any] = {"schema": {"type": "string"}}
                if isinstance(route.data, str):
                    content["example"] = route.data
                request_body["content"] = {"text/plain": content}

            operation["requestBody"] = request_body

        operation["responses"]["200"] = collector.response_schema(
            route.response_model
        )

        if route.responses:
            for status_code, response_config in route.responses.items():
                model = response_config.get("model")
                operation["responses"][str(status_code)] = (
                    collector.error_response_schema(status_code, model)
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

    info: dict[str, Any] = {"title": title, "version": version}
    if description:
        info["description"] = description

    components: dict[str, Any] = {"schemas": collector.schemas}
    if security_schemes:
        components["securitySchemes"] = security_schemes

    openapi_schema: dict[str, Any] = {
        "openapi": "3.0.3",
        "info": info,
        "paths": paths,
        "components": components,
    }

    if server_url:
        openapi_schema["servers"] = [
            {
                "url": server_url,
                "description": "FastHTTP Proxy",
            }
        ]

    return openapi_schema
