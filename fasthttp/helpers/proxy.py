"""Helpers for proxy URLs."""

from urllib.parse import urlsplit, urlunsplit


def mask_proxy_url(proxy: str) -> str:
    """Return a proxy URL that is safe to log.

    Replaces the password in ``http://user:pass@host:port`` with ``***``.
    URLs without a password are returned unchanged.
    """
    try:
        parts = urlsplit(proxy)
        if parts.password is None:
            return proxy
        host = parts.hostname or ""
        if ":" in host:  # IPv6 literal
            host = f"[{host}]"
        netloc = f"{parts.username or ''}:***@{host}"
        if parts.port is not None:
            netloc += f":{parts.port}"
        return urlunsplit(parts._replace(netloc=netloc))
    except ValueError:
        return "***"
