from __future__ import annotations


def normalize_docs_base_url(base_url: str = "") -> str:
    """
    Normalize a documentation URL prefix.

    This helper converts values like `api`, `/api/`, or `/`
    into a predictable prefix used by the docs endpoints.

    Examples:
        "" -> ""
        "/" -> ""
        "api" -> "/api"
        "/api/" -> "/api"
    """
    normalized = base_url.strip()
    if not normalized or normalized == "/":
        return ""

    normalized = "/" + normalized.strip("/")
    return normalized


def build_docs_urls(base_url: str = "") -> dict[str, str]:
    """
    Build documentation URLs with an optional shared prefix.

    Returns a dictionary with:
    - base_url
    - docs_url
    - openapi_url
    - request_url
    """
    prefix = normalize_docs_base_url(base_url)
    return {
        "base_url": prefix,
        "docs_url": f"{prefix}/docs",
        "openapi_url": f"{prefix}/openapi.json",
        "request_url": f"{prefix}/request",
    }
