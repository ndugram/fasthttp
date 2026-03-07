import logging
from urllib.parse import urlparse

from .ssrf import SSRFProtection, SSRFBlockedError
from .secrets import SecretsMasking
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from .headers import HeaderProtection
from .response import ResponseProtection, ResponseProtectionConfig
from .limits import Limits, LimitsConfig
from .redirect import RedirectProtection, RedirectConfig

logger = logging.getLogger("fasthttp.security")


class Security:
    def __init__(
        self,
        limits_config: LimitsConfig | None = None,
        response_config: ResponseProtectionConfig | None = None,
        redirect_config: RedirectConfig | None = None,
        circuit_breaker_config: CircuitBreakerConfig | None = None,
    ):
        self._ssrf = SSRFProtection()
        self._secrets = SecretsMasking()
        self._circuit_breaker = CircuitBreaker(circuit_breaker_config)
        self._headers = HeaderProtection()
        self._response = ResponseProtection(response_config)
        self._limits = Limits(limits_config)
        self._redirect = RedirectProtection(redirect_config)

    async def pre_request(self, url: str, method: str) -> None:
        self._ssrf.validate_request(url)

        if not self._limits.validate_url_length(url):
            raise SecurityError(f"URL too long: {len(url)} chars")

        parsed = urlparse(url)
        can_proceed = await self._circuit_breaker.can_proceed(parsed.netloc)
        if not can_proceed:
            raise CircuitOpenError(f"Circuit breaker open for: {parsed.netloc}")

        await self._limits.cooldown()

    def sanitize_request_headers(self, headers: dict[str, str]) -> dict[str, str]:
        return self._headers.sanitize_request_headers(headers)

    async def post_request(
        self, url: str, method: str, success: bool, error: Exception | None = None
    ) -> None:
        parsed = urlparse(url)
        host = parsed.netloc

        if success:
            await self._circuit_breaker.record_success(host)
        else:
            await self._circuit_breaker.record_failure(host)

    def check_response(
        self,
        content: bytes,
        content_type: str | None = None,
        status_code: int = 200,
    ) -> None:
        valid, error = self._response.validate_response(
            content=content, content_type=content_type, status_code=status_code
        )
        if not valid:
            raise SecurityError(error)

    def check_response_headers(self, headers: dict[str, str]) -> None:
        valid, error = self._headers.check_response_headers(headers)
        if not valid:
            raise SecurityError(error)

    def check_redirect(
        self, original_url: str, redirect_url: str, method: str = "GET"
    ) -> None:
        valid, error = self._redirect.check_redirect(
            original_url, redirect_url, method
        )
        if not valid:
            raise SecurityError(error)

    def reset_redirects(self) -> None:
        self._redirect.reset()

    def mask_for_logging(self, data: str) -> str:
        return self._secrets.mask_log_message(data)

    def mask_headers_for_logging(self, headers: dict[str, str]) -> dict[str, str]:
        return self._secrets.mask_headers(headers)

    @property
    def timeout(self) -> float:
        return self._limits.timeout

    @property
    def connect_timeout(self) -> float:
        return self._limits.connect_timeout

    @property
    def max_response_size(self) -> int:
        return self._limits.max_response_size

    @property
    def max_redirects(self) -> int:
        return self._limits.max_redirects

    async def acquire_slot(self) -> None:
        await self._limits.acquire()

    def release_slot(self) -> None:
        self._limits.release()

    def get_circuit_state(self, host: str):
        return self._circuit_breaker.get_state(host)


class SecurityError(Exception):
    pass


class CircuitOpenError(SecurityError):
    pass
