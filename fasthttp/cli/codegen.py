from __future__ import annotations

import keyword
import re
from pathlib import Path
from typing import Any

import httpx
import orjson

_JSON_TYPE_MAP = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
}

_HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head", "options")


class CodegenError(Exception):
    """Raised when a spec can't be loaded or parsed."""


def load_spec(source: str) -> dict[str, Any]:
    """Load an OpenAPI spec from a URL or local file path (JSON or YAML)."""
    if source.startswith(("http://", "https://")):
        try:
            text = httpx.get(source, timeout=15, follow_redirects=True).raise_for_status().text
        except httpx.HTTPError as e:
            msg = f"Failed to fetch spec from {source}: {e}"
            raise CodegenError(msg) from e
    else:
        path = Path(source)
        if not path.exists():
            msg = f"Spec file not found: {source}"
            raise CodegenError(msg)
        text = path.read_text()

    stripped = text.lstrip()
    if stripped.startswith("{"):
        return orjson.loads(text)

    try:
        import yaml  # type: ignore
    except ImportError as e:
        msg = (
            "Spec looks like YAML but PyYAML isn't installed. "
            "Run `pip install pyyaml`, or pass a JSON spec instead."
        )
        raise CodegenError(msg) from e
    return yaml.safe_load(text)


def _to_snake_case(name: str) -> str:
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    name = name.strip("_").lower()
    return name or "operation"


def _to_pascal_case(name: str) -> str:
    parts = re.split(r"[^0-9a-zA-Z]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Model"


def _safe_identifier(name: str, *, fallback: str) -> str:
    ident = re.sub(r"\W", "_", name)
    if not ident or ident[0].isdigit():
        ident = f"_{ident}"
    if keyword.iskeyword(ident):
        ident = f"{ident}_"
    return ident or fallback


def _default_op_id(method: str, path: str) -> str:
    return f"{method}_{path}"


def _ref_name(ref: str) -> str:
    return _to_pascal_case(ref.rsplit("/", 1)[-1])


def python_type(schema: dict[str, Any] | None, *, required: bool = True) -> str:
    """Map a JSON Schema fragment to a Python type annotation string."""
    if not schema:
        return "Any" if required else "Any | None"

    if "$ref" in schema:
        t = _ref_name(schema["$ref"])
    elif schema.get("enum") and schema.get("type") == "string":
        values = ", ".join(repr(v) for v in schema["enum"])
        t = f"Literal[{values}]"
    elif schema.get("type") == "array":
        t = f"list[{python_type(schema.get('items'))}]"
    elif schema.get("type") == "object":
        t = "dict[str, Any]"
    elif schema.get("type") in _JSON_TYPE_MAP:
        t = _JSON_TYPE_MAP[schema["type"]]
    elif any(k in schema for k in ("oneOf", "anyOf", "allOf")):
        t = "Any"
    else:
        t = "Any"

    if schema.get("nullable") or not required:
        t = f"{t} | None"
    return t


def generate_model(name: str, schema: dict[str, Any]) -> str:
    class_name = _to_pascal_case(name)
    props: dict[str, Any] = schema.get("properties", {})
    required = set(schema.get("required", []))

    lines = [f"class {class_name}(BaseModel):"]
    if not props:
        lines.append("    pass")
        return "\n".join(lines)

    for prop_name, prop_schema in props.items():
        is_required = prop_name in required
        py_name = _safe_identifier(prop_name, fallback="field")
        annotation = python_type(prop_schema, required=is_required)

        if py_name != prop_name:
            lines.append(
                f'    {py_name}: {annotation} = Field(alias="{prop_name}"{"" if is_required else ", default=None"})'
            )
        else:
            default = "" if is_required else " = None"
            lines.append(f"    {py_name}: {annotation}{default}")

    return "\n".join(lines)


def collect_models(spec: dict[str, Any]) -> list[str]:
    schemas: dict[str, Any] = spec.get("components", {}).get("schemas", {})
    models = []
    for name, schema in schemas.items():
        if schema.get("type") == "object" or "properties" in schema:
            models.append(generate_model(name, schema))
    return models


def _success_response_model(op: dict[str, Any]) -> str | None:
    responses = op.get("responses", {})
    for code, resp in responses.items():
        if not str(code).startswith("2"):
            continue
        content = (resp or {}).get("content", {}).get("application/json", {})
        schema = content.get("schema")
        if schema and "$ref" in schema:
            return _ref_name(schema["$ref"])
    return None


def _request_body_model(op: dict[str, Any]) -> str | None:
    body = op.get("requestBody", {})
    content = body.get("content", {}).get("application/json", {})
    schema = content.get("schema")
    if schema and "$ref" in schema:
        return _ref_name(schema["$ref"])
    return None


def generate_operation(path: str, method: str, op: dict[str, Any]) -> str:
    op_id = op.get("operationId") or _default_op_id(method, path)
    func_name = _to_snake_case(op_id)
    summary = (op.get("summary") or op.get("description") or "").strip()

    parameters = op.get("parameters", [])
    path_params = [p["name"] for p in parameters if p.get("in") == "path"]
    query_params = [p["name"] for p in parameters if p.get("in") == "query"]

    response_model = _success_response_model(op)
    body_model = _request_body_model(op)
    tags = op.get("tags") or []

    if path_params:
        return _generate_imperative(
            func_name, path, method, path_params, query_params, body_model, summary
        )
    return _generate_decorated_route(
        func_name, path, method, query_params, body_model, response_model, tags, summary
    )


def _generate_decorated_route(
    func_name: str,
    path: str,
    method: str,
    query_params: list[str],
    body_model: str | None,
    response_model: str | None,
    tags: list[str],
    summary: str,
) -> str:
    kwargs = ['url="' + path + '"']
    if tags:
        kwargs.append(f"tags={tags!r}")
    if response_model:
        kwargs.append(f"response_model={response_model}")
    kwargs_str = ", ".join(kwargs)

    doc = f'\n    """{summary}"""' if summary else ""

    if body_model:
        signature = f"async def {func_name}(resp: Response, body: {body_model}) -> dict:{doc}"
        return_expr = 'return {"json": body.model_dump(mode="json", exclude_none=True)}'
    else:
        signature = f"async def {func_name}(resp: Response) -> dict:{doc}"
        return_expr = "return resp.json()"

    params_hint = (
        f"  # query params: {', '.join(query_params)} — pass via params={{...}}"
        if query_params
        else ""
    )

    return f"@app.{method}({kwargs_str}){params_hint}\n{signature}\n    {return_expr}\n"


def _generate_imperative(
    func_name: str,
    path: str,
    method: str,
    path_params: list[str],
    query_params: list[str],
    body_model: str | None,
    summary: str,
) -> str:
    args = ", ".join(f"{p}: str" for p in path_params)
    if body_model:
        args = f"{args}, body: {body_model}" if args else f"body: {body_model}"

    doc = f'\n    """{summary}"""' if summary else ""
    params_kw = ""
    if query_params:
        params_kw = f"  # query params: {', '.join(query_params)} — pass params={{...}} to session.{method}(...)"

    call = f'await session.{method}(f"{{base_url}}{path}"'
    if body_model:
        call += ', json=body.model_dump(mode="json", exclude_none=True)'
    call += ")"

    return (
        f"async def {func_name}(session: AsyncSession, {args}) -> dict | None:{doc}  "
        f"# no static route: has path params{params_kw}\n"
        f"    resp = {call}\n"
        f"    return resp.json() if resp else None\n"
    )


def generate_client(spec: dict[str, Any]) -> str:
    info = spec.get("info", {})
    title = info.get("title", "API")
    servers = spec.get("servers", [])
    base_url = servers[0]["url"] if servers else "https://api.example.com"

    models = collect_models(spec)

    decorated_routes: list[str] = []
    imperative_funcs: list[str] = []

    for path, path_item in spec.get("paths", {}).items():
        for method in _HTTP_METHODS:
            op = path_item.get(method)
            if not op:
                continue
            code = generate_operation(path, method, op)
            if code.startswith("@app."):
                decorated_routes.append(code)
            else:
                imperative_funcs.append(code)

    parts = [
        '"""',
        f"Generated by `fasthttp codegen` from: {title}",
        "",
        "MVP limitations:",
        "- oneOf/anyOf/allOf schemas fall back to Any",
        "- inline (unnamed) nested objects fall back to dict[str, Any]",
        "- only the first 2xx response and application/json bodies are used",
        "- endpoints with path parameters use AsyncSession (fasthttp has no",
        "  dynamic path routing — a route's URL is fixed at decoration time)",
        '"""',
        "",
        "from typing import Any, Literal",
        "",
        "from pydantic import BaseModel, Field",
        "",
        "from fasthttp import AsyncSession, FastHTTP",
        "from fasthttp.response import Response",
        "",
        f'base_url = "{base_url}"',
        "app = FastHTTP(base_url=base_url, security=True)",
        "",
    ]

    if models:
        parts.append("\n\n".join(models))
        parts.append("")

    if decorated_routes:
        parts.append("\n\n".join(decorated_routes))
        parts.append("")

    if imperative_funcs:
        parts.append("# --- endpoints with path parameters (no static route possible) ---\n")
        parts.append("\n\n".join(imperative_funcs))
        parts.append("")

    parts.append('if __name__ == "__main__":\n    app.run()  # runs every @app.<method> route above\n')

    return "\n".join(parts)
