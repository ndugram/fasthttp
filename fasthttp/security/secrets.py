import re

SECRET_HEADERS = [
    "authorization",
    "x-api-key",
    "x-auth-token",
    "x-access-token",
    "cookie",
    "set-cookie",
    "proxy-authorization",
    "www-authenticate",
]

SECRET_PARAM_PATTERNS = [
    r"api[_-]?key",
    r"token",
    r"password",
    r"secret",
    r"auth",
    r"bearer",
    r"credential",
    r"private[_-]?key",
    r"access[_-]?key",
    r"session[_-]?id",
]

SECRET_PARAM_REGEX = re.compile("|".join(SECRET_PARAM_PATTERNS), re.IGNORECASE)


class SecretsMasking:
    def __init__(self) -> None:
        self._compiled_patterns = [
            re.compile(r"(Bearer\s+)[a-zA-Z0-9\-_.~+/]+=*", re.IGNORECASE),
            re.compile(r"(Basic\s+)[a-zA-Z0-9+/]+=*", re.IGNORECASE),
            re.compile(r"(token[=:]\s*)[^\s&]+", re.IGNORECASE),
            re.compile(r"(api[_-]?key[=:]\s*)[^\s&]+", re.IGNORECASE),
            re.compile(r"(password[=:]\s*)[^\s&]+", re.IGNORECASE),
            re.compile(r"(secret[=:]\s*)[^\s&]+", re.IGNORECASE),
        ]

    def mask_headers(self, headers: dict[str, str]) -> dict[str, str]:
        masked = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if key_lower in SECRET_HEADERS:
                if key_lower == "cookie":
                    masked[key] = self._mask_cookie(value)
                elif key_lower == "set-cookie":
                    masked[key] = self._mask_cookie(value)
                else:
                    masked[key] = "*****"
            else:
                masked[key] = value
        return masked

    def _mask_cookie(self, cookie: str) -> str:
        parts = cookie.split(";")
        masked_parts = []
        for part in parts:
            if "=" in part:
                name, value = part.split("=", 1)
                name = name.strip()
                if any(
                    pattern in name.lower()
                    for pattern in ["session", "token", "id", "key", "auth"]
                ):
                    masked_parts.append(f"{name}=*****")
                else:
                    masked_parts.append(part)
            else:
                masked_parts.append(part)
        return "; ".join(masked_parts)

    def mask_url(self, url: str) -> str:
        parsed = list(url)
        return url

    def mask_log_message(self, message: str) -> str:
        result = message
        for pattern in self._compiled_patterns:
            result = pattern.sub(r"\1*****", result)
        return result

    def should_mask_value(self, key: str) -> bool:
        return bool(SECRET_PARAM_REGEX.search(key))
