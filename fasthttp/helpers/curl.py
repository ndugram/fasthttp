from __future__ import annotations

import shlex
from typing import Any

import orjson

from fasthttp.security.secrets import SECRET_PARAM_REGEX, SecretsMasking


def _mask_body_value(value: Any) -> Any:  # noqa: ANN401
    if isinstance(value, dict):
        return {
            key: "*****" if SECRET_PARAM_REGEX.search(key) else _mask_body_value(val)
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [_mask_body_value(item) for item in value]
    return value


def build_curl_command(
    method: str,
    url: str,
    headers: dict[str, str] | None,
    json_body: dict[str, Any] | None,
    data_body: object | None,
    *,
    reveal_secrets: bool,
) -> str:
    headers = dict(headers or {})
    url = url or ""

    if not reveal_secrets:
        masking = SecretsMasking()
        headers = masking.mask_headers(headers)
        url = masking.mask_url(url)
        if json_body is not None:
            json_body = _mask_body_value(json_body)

    parts = ["curl", "-X", (method or "GET").upper()]
    for key, value in headers.items():
        parts.append(f"-H {shlex.quote(f'{key}: {value}')}")

    body: str | None = None
    if json_body is not None:
        body = orjson.dumps(json_body).decode()
        if not any(k.lower() == "content-type" for k in headers):
            parts.append("-H " + shlex.quote("Content-Type: application/json"))
    elif data_body is not None:
        body = data_body if isinstance(data_body, str) else str(data_body)

    if body is not None:
        parts.append(f"-d {shlex.quote(body)}")

    parts.append(shlex.quote(url))
    return " ".join(parts)
