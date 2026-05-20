from __future__ import annotations

try:
    from fasthttp._core import (
        apply_base_url as _rs_apply_base_url,
        check_https_url as _rs_check_https_url,
        join_prefix as _rs_join_prefix,
        resolve_url as _rs_resolve_url,
    )

    def check_https_url(*, url: str) -> str:
        return _rs_check_https_url(url)

    def join_prefix(prefix: str, url: str) -> str:
        return _rs_join_prefix(prefix, url)

    def resolve_url(*, url: str, base_url: str | None, prefix: str) -> str:
        return _rs_resolve_url(url, base_url, prefix)

    def apply_base_url(*, url: str, base_url: str | None) -> str:
        return _rs_apply_base_url(url, base_url)

except ImportError:
    # Pure-Python fallback when the Rust extension is not compiled.
    from urllib.parse import urljoin as _urljoin

    def check_https_url(*, url: str) -> str:
        url = url.strip()
        if url.startswith(("https://", "http://")):
            return url
        return f"https://{url}"

    def join_prefix(prefix: str, url: str) -> str:
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
        url = url.strip()
        if url.startswith(("https://", "http://")):
            return url
        if base_url is None:
            if url.startswith("/"):
                msg = f"Relative URL requires base_url. Got url={url!r} without base_url."
                raise ValueError(msg)
            return check_https_url(url=url)
        base_url = check_https_url(url=base_url)
        base = base_url.rstrip("/") + "/"
        path = join_prefix(prefix, url).lstrip("/")
        return _urljoin(base, path)

    def apply_base_url(*, url: str, base_url: str | None) -> str:
        url = url.strip()
        if url.startswith(("https://", "http://")):
            return url
        if base_url:
            return check_https_url(url=f"{base_url.rstrip('/')}/{url.lstrip('/')}")
        return check_https_url(url=url)


__all__ = (
    "apply_base_url",
    "check_https_url",
    "join_prefix",
    "resolve_url",
)
