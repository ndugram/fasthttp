import asyncio
from dataclasses import dataclass


@dataclass
class LimitsConfig:
    timeout: float = 30.0
    connect_timeout: float = 10.0
    max_response_size_mb: int = 100
    max_redirects: int = 10
    max_url_length: int = 8192
    max_concurrent_requests: int = 100
    request_cooldown_ms: int = 0


class Limits:
    def __init__(
        self,
        config: LimitsConfig | None = None
    ) -> None:
        self._config = config or LimitsConfig()
        self._semaphore: asyncio.Semaphore | None = (
            asyncio.Semaphore(self._config.max_concurrent_requests)
            if self._config.max_concurrent_requests > 0
            else None
        )
        self._last_request_time = 0.0
        self._cooldown_lock = asyncio.Lock()

    @property
    def timeout(self) -> float:
        return self._config.timeout

    @property
    def connect_timeout(self) -> float:
        return self._config.connect_timeout

    @property
    def max_response_size(self) -> int:
        return self._config.max_response_size_mb * 1024 * 1024

    @property
    def max_redirects(self) -> int:
        return self._config.max_redirects

    @property
    def max_url_length(self) -> int:
        return self._config.max_url_length

    def validate_url_length(self, url: str) -> bool:
        return len(url) <= self._config.max_url_length

    async def acquire(self) -> None:
        if self._semaphore:
            await self._semaphore.acquire()

    def release(self) -> None:
        if self._semaphore:
            self._semaphore.release()

    async def cooldown(self) -> None:
        if self._config.request_cooldown_ms > 0:
            async with self._cooldown_lock:
                import time

                now = time.time()
                min_interval = self._config.request_cooldown_ms / 1000.0
                time_since_last = now - self._last_request_time
                if time_since_last < min_interval:
                    await asyncio.sleep(min_interval - time_since_last)
                self._last_request_time = time.time()
