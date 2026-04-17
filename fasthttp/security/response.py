import re
from dataclasses import dataclass

DANGEROUS_CONTENT_TYPES = [
    "text/html",
    "application/xhtml+xml",
]

XSS_PATTERNS = [
    re.compile(r"<script[^>]*>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
    re.compile(r"<iframe[^>]*>", re.IGNORECASE),
    re.compile(r"<object[^>]*>", re.IGNORECASE),
    re.compile(r"<embed[^>]*>", re.IGNORECASE),
    re.compile(r"<applet[^>]*>", re.IGNORECASE),
    re.compile(r"vbscript:", re.IGNORECASE),
    re.compile(r"data:text/html", re.IGNORECASE),
]

HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
SCRIPT_TAG_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
EVENT_HANDLER_PATTERN = re.compile(r"\s+on\w+\s*=\s*[\"']", re.IGNORECASE)


@dataclass
class ResponseProtectionConfig:
    max_size_mb: int = 100
    sanitize_html: bool = True
    block_dangerous_content: bool = True
    allowed_content_types: list | None  = None


class ResponseProtection:
    def __init__(
        self,
        config: ResponseProtectionConfig | None = None
    ) -> None:
        self._config = config or ResponseProtectionConfig()
        self._dangerous_content_types = [
            ct.lower() for ct in DANGEROUS_CONTENT_TYPES
        ]

    def check_size(
        self,
        size_bytes: int
    ) -> tuple[bool, str | None]:
        max_bytes = self._config.max_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            return False, f"Response too large: {size_bytes} bytes (max: {max_bytes})"
        return True, None

    def check_content_type(
        self,
        content_type: str | None,
        expected_type: str | None = None
    ) -> tuple[bool, str | None]:
        if not content_type:
            return True, None

        content_type_lower = content_type.lower().split(";")[0].strip()

        if self._config.block_dangerous_content:
            if content_type_lower in self._dangerous_content_types:
                if expected_type and expected_type.lower() != content_type_lower:
                    return (
                        False,
                        f"Unexpected content type: expected {expected_type}, got {content_type_lower}",
                    )

        if self._config.allowed_content_types:
            allowed = [ct.lower() for ct in self._config.allowed_content_types]
            if content_type_lower not in allowed:
                return False, f"Content type {content_type_lower} not allowed"

        return True, None

    def sanitize_html(self, content: str) -> str:
        if not self._config.sanitize_html:
            return content

        result = content

        result = SCRIPT_TAG_PATTERN.sub("", result)

        result = HTML_TAG_PATTERN.sub("", result)

        return result

    def detect_xss(self, content: str) -> tuple[bool, str | None]:
        for pattern in XSS_PATTERNS:
            if pattern.search(content):
                return True, "Potential XSS detected in response"

        if EVENT_HANDLER_PATTERN.search(content):
            return True, "Potential XSS (event handler) detected in response"

        return False, None

    def validate_response(
        self,
        content: bytes,
        content_type: str | None = None,
        status_code: int = 200,
    ) -> tuple[bool, str | None]:
        size_check = self.check_size(len(content))
        if not size_check[0]:
            return size_check

        if content_type:
            ct_check = self.check_content_type(content_type)
            if not ct_check[0]:
                return ct_check

        if b"<" in content and b">" in content:
            try:
                text = content.decode("utf-8", errors="ignore")
                xss_check = self.detect_xss(text)
                if xss_check[0]:
                    return False, xss_check[1]
            except Exception:
                pass

        return True, None
