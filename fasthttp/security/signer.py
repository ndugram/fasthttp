import hmac
import secrets
import time
from typing import Any

try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False


class RequestSigner:
    def __init__(self, secret_key: bytes | None = None) -> None:
        self._secret_key = secret_key or secrets.token_bytes(32)
        self._max_age = 300

    def _serialize_body(self, body: Any) -> bytes:
        if body is None:
            return b""
        if isinstance(body, dict) or isinstance(body, list):
            if ORJSON_AVAILABLE:
                return orjson.dumps(body, option=orjson.OPT_SORT_KEYS)
            import json
            return json.dumps(body, sort_keys=True).encode("utf-8")
        if isinstance(body, str):
            return body.encode("utf-8")
        if isinstance(body, bytes):
            return body
        return b""

    def _create_payload(self, method: str, url: str, timestamp: int, body: bytes) -> bytes:
        url_str = str(url)
        body_str = body.decode("utf-8") if body else ""
        return f"{method}\n{url_str}\n{timestamp}\n{body_str}".encode("utf-8")

    def sign(self, method: str, url: str | Any, body: Any) -> dict[str, str]:
        timestamp = int(time.time())
        nonce = secrets.token_hex(16)
        body_bytes = self._serialize_body(body)
        payload = self._create_payload(method, url, timestamp, body_bytes)
        signature = hmac.new(self._secret_key, payload, digestmod="sha256").hexdigest()
        return {
            "X-Signature": signature,
            "X-Timestamp": str(timestamp),
            "X-Nonce": nonce
        }

    def verify(self, method: str, url: str, timestamp: int, body: Any, signature: str) -> bool:
        if abs(time.time() - timestamp) > self._max_age:
            return False
        body_bytes = self._serialize_body(body)
        payload = self._create_payload(method, url, timestamp, body_bytes)
        expected = hmac.new(self._secret_key, payload, digestmod="sha256").hexdigest()
        return hmac.compare_digest(expected, signature)
