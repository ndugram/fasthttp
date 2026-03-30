from __future__ import annotations

import inspect
from collections.abc import Callable
from urllib.parse import urljoin


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
                f"Parameter '{name}' in function '{func.__name__}'"
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
            f"Function '{func.__name__}' must explicitly"
            "define return type annotation"
        )
        raise TypeError(msg)


def check_https_url(*, url: str) -> str:
    """
    Normalize URL scheme.

    If a URL has no scheme, https:// is assumed.

    Args:
        url: Input URL.

    Returns:
        URL with an explicit scheme.
    """
    url = url.strip()
    if url.startswith(("https://", "http://")):
        return url
    return f"https://{url}"


def join_prefix(prefix: str, url: str) -> str:
    """
    Join a path prefix and a URL/path fragment.

    This function is path-oriented. It does not try to parse full URLs.

    Args:
        prefix: Path prefix. Can be empty, with or without leading/trailing slash.
        url: Path fragment. Can be empty or start with a slash.

    Returns:
        A normalized joined path (starts with / unless empty input is given).
    """
    prefix = prefix.strip()
    url = url.strip()
    if not prefix:
        return url

    if not prefix.startswith("/"):
        prefix = f"/{prefix}"
    if prefix != "/" and prefix.endswith("/"):
        prefix = prefix[:-1]

    if not url.startswith("/"):
        url = f"/{url}"

    if url == "/":
        return prefix or "/"
    return f"{prefix}{url}"


def resolve_url(*, url: str, base_url: str | None, prefix: str) -> str:
    """
    Resolve a route URL against base_url and prefix.

    Rules:
    - If url is absolute (http/https), it is returned unchanged.
    - If url is a path (starts with /), base_url is required.
    - If base_url is provided, the final URL is base_url + prefix + url.
    - If base_url is not provided and url is not a path, https:// is assumed.

    Args:
        url: Absolute URL or relative fragment.
        base_url: Base URL for relative paths.
        prefix: Prefix applied before the route url.

    Returns:
        Fully-qualified URL.

    Raises:
        ValueError: If url is a path (starts with /) and base_url is missing.
    """
    url = url.strip()
    if url.startswith(("https://", "http://")):
        return url

    if base_url is None:
        if url.startswith("/"):
            msg = (
                "Relative URL requires base_url. "
                f"Got url={url!r} without base_url."
            )
            raise ValueError(msg)
        return check_https_url(url=url)

    base_url = check_https_url(url=base_url)
    base = base_url.rstrip("/") + "/"
    path = join_prefix(prefix, url).lstrip("/")
    return urljoin(base, path)


def apply_base_url(*, url: str, base_url: str | None) -> str:
    url = url.strip()
    if url.startswith(("https://", "http://")):
        return url

    if base_url:
        return check_https_url(url=f"{base_url.rstrip('/')}/{url.lstrip('/')}")

    return check_https_url(url=url)


__all__ = (
    "apply_base_url",
    "check_annotated_parameters",
    "check_annotated_return",
    "check_https_url",
    "join_prefix",
    "resolve_url",
)
