import hmac
import secrets
import time
from typing import Any

try:
    import orjson

    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False

try:
    from fasthttp._core import sign_request as _rs_sign_request  # type: ignore
    from fasthttp._core import verify_request as _rs_verify_request  # type: ignore

    _RUST = True
except ImportError:
    _RUST = False


class RequestSigner:
    def __init__(self, secret_key: bytes | None = None) -> None:
        self._secret_key = secret_key or secrets.token_bytes(32)
        self._max_age = 300

    def _serialize_body(self, body: Any) -> bytes:  # noqa: ANN401
        if body is None:
            return b""
        if isinstance(body, (dict, list)):
            if ORJSON_AVAILABLE:
                return orjson.dumps(body, option=orjson.OPT_SORT_KEYS)
            import json

            return json.dumps(body, sort_keys=True).encode("utf-8")
        if isinstance(body, str):
            return body.encode("utf-8")
        if isinstance(body, bytes):
            return body
        return b""

    def _create_payload(
        self, method: str, url: str, timestamp: int, body: bytes
    ) -> bytes:
        url_str = str(url)
        body_str = body.decode("utf-8") if body else ""
        return f"{method}\n{url_str}\n{timestamp}\n{body_str}".encode()

    def sign(self, method: str, url: str | Any, body: Any) -> dict[str, str]:  # noqa: ANN401
        body_bytes = self._serialize_body(body)
        if _RUST:
            return _rs_sign_request(self._secret_key, method, str(url), body_bytes)
        timestamp = int(time.time())
        nonce = secrets.token_hex(16)
        payload = self._create_payload(method, url, timestamp, body_bytes)
        signature = hmac.new(self._secret_key, payload, digestmod="sha256").hexdigest()
        return {
            "X-Signature": signature,
            "X-Timestamp": str(timestamp),
            "X-Nonce": nonce,
        }

    def verify(
        self,
        method: str,
        url: str,
        timestamp: int,
        body: dict | list | str | bytes | None,
        signature: str,
    ) -> bool:
        body_bytes = self._serialize_body(body)
        if _RUST:
            return _rs_verify_request(
                self._secret_key,
                method,
                str(url),
                timestamp,
                body_bytes,
                signature,
                self._max_age,
            )
        if abs(time.time() - timestamp) > self._max_age:
            return False
        payload = self._create_payload(method, url, timestamp, body_bytes)
        expected = hmac.new(self._secret_key, payload, digestmod="sha256").hexdigest()
        return hmac.compare_digest(expected, signature)
