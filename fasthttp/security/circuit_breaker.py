import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 30.0
    half_open_max_calls: int = 3


@dataclass
class HostState:
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    half_open_calls: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig | None = None) -> None:
        self._config = config or CircuitBreakerConfig()
        self._hosts: dict[str, HostState] = {}
        self._lock = asyncio.Lock()

    async def can_proceed(self, host: str) -> bool:
        async with self._lock:
            if host not in self._hosts:
                self._hosts[host] = HostState()

            state = self._hosts[host]

            if state.state == CircuitState.CLOSED:
                return True

            if state.state == CircuitState.OPEN:
                if time.time() - state.last_failure_time >= self._config.timeout:
                    state.state = CircuitState.HALF_OPEN
                    state.half_open_calls = 0
                    return True
                return False

            if state.state == CircuitState.HALF_OPEN:
                if state.half_open_calls < self._config.half_open_max_calls:
                    state.half_open_calls += 1
                    return True
                return False

            return True

    async def record_success(self, host: str) -> None:
        async with self._lock:
            if host not in self._hosts:
                return

            state = self._hosts[host]

            if state.state == CircuitState.HALF_OPEN:
                state.success_count += 1
                if state.success_count >= self._config.success_threshold:
                    state.state = CircuitState.CLOSED
                    state.failure_count = 0
                    state.success_count = 0
            elif state.state == CircuitState.CLOSED:
                state.failure_count = 0

    async def record_failure(self, host: str) -> None:
        async with self._lock:
            if host not in self._hosts:
                self._hosts[host] = HostState()

            state = self._hosts[host]
            state.failure_count += 1
            state.last_failure_time = time.time()

            if state.state == CircuitState.HALF_OPEN:
                state.state = CircuitState.OPEN
                state.half_open_calls = 0
            elif state.failure_count >= self._config.failure_threshold:
                state.state = CircuitState.OPEN

    def get_state(self, host: str) -> CircuitState | None:
        if host in self._hosts:
            return self._hosts[host].state
        return None
