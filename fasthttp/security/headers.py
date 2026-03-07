import re

DANGEROUS_RESPONSE_HEADERS = [
    "x-accel-redirect",
    "x-sendfile",
    "x-accel-limit-rate",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "refresh",
    "content-security-policy",
    "content-security-policy-report-only",
]

BLOCKED_REQUEST_HEADERS = [
    "host",
    "content-length",
    "transfer-encoding",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "upgrade",
]

CRLF_PATTERN = re.compile(r"[\r\n]")


class HeaderProtection:
    def __init__(self) -> None:
        self._dangerous_headers = [
            h.lower() for h in DANGEROUS_RESPONSE_HEADERS
            ]
        self._blocked_request = [
            h.lower() for h in BLOCKED_REQUEST_HEADERS
            ]

    def sanitize_request_headers(
        self,
        headers: dict[str, str]
    ) -> dict[str, str]:
        sanitized = {}
        for key, value in headers.items():
            key_clean = self._sanitize_header_name(key)
            value_clean = self._sanitize_header_value(value)
            if key_clean and value_clean:
                sanitized[key_clean] = value_clean
        return sanitized

    def _sanitize_header_name(
        self,
        name: str
    ) -> str | None:
        cleaned = name.strip()
        cleaned = CRLF_PATTERN.sub("", cleaned)
        if not cleaned or cleaned.lower() in self._blocked_request:
            return None
        return cleaned

    def _sanitize_header_value(
        self,
        value: str
    ) -> str | None:
        cleaned = value.strip()
        cleaned = CRLF_PATTERN.sub("", cleaned)
        return cleaned if cleaned else None

    def check_response_headers(
        self,
        headers: dict[str, str]
    ) -> tuple[bool, str | None]:
        for key, value in headers.items():
            key_lower = key.lower()

            if key_lower in self._dangerous_headers:
                return False, f"Dangerous header detected: {key}"

            if CRLF_PATTERN.search(value):
                return False, f"CRLF injection detected in header: {key}"

            if key_lower == "set-cookie":
                cookie_check = self._check_cookie_security(value)
                if not cookie_check[0]:
                    return cookie_check

        return True, None

    def _check_cookie_security(
        self, cookie: str
    ) -> tuple[bool, str | None]:
        parts = cookie.lower().split(";")
        has_secure = any("secure" in p.strip() for p in parts)
        has_httponly = any("httponly" in p.strip() for p in parts)
        has_samesite = any("samesite" in p.strip() for p in parts)

        if has_samesite:
            for part in parts:
                if "samesite=none" in part and not has_secure:
                    return False, "Cookie with SameSite=None without Secure flag"

        return True, None

    def validate_host_header(
        self,
        actual_host: str,
        expected_host: str
    ) -> bool:
        return actual_host.lower() == expected_host.lower()
