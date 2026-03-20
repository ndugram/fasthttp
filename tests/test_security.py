"""Tests for security modules."""
import pytest
import asyncio

from fasthttp.security.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    HostState,
)


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig dataclass."""

    def test_config_defaults(self) -> None:
        """Test CircuitBreakerConfig default values."""
        config = CircuitBreakerConfig()

        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout == 30.0
        assert config.half_open_max_calls == 3

    def test_config_custom_values(self) -> None:
        """Test CircuitBreakerConfig with custom values."""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            success_threshold=5,
            timeout=60.0,
            half_open_max_calls=5,
        )

        assert config.failure_threshold == 10
        assert config.success_threshold == 5
        assert config.timeout == 60.0
        assert config.half_open_max_calls == 5


class TestHostState:
    """Tests for HostState dataclass."""

    def test_host_state_defaults(self) -> None:
        """Test HostState default values."""
        state = HostState()

        assert state.state == CircuitState.CLOSED
        assert state.failure_count == 0
        assert state.success_count == 0
        assert state.last_failure_time == 0.0
        assert state.half_open_calls == 0
        assert isinstance(state.lock, asyncio.Lock)

    def test_host_state_custom_values(self) -> None:
        """Test HostState with custom values."""
        state = HostState(
            state=CircuitState.OPEN,
            failure_count=5,
            success_count=2,
            last_failure_time=100.0,
            half_open_calls=1,
        )

        assert state.state == CircuitState.OPEN
        assert state.failure_count == 5
        assert state.success_count == 2
        assert state.last_failure_time == 100.0
        assert state.half_open_calls == 1


class TestCircuitState:
    """Tests for CircuitState enum."""

    def test_circuit_state_values(self) -> None:
        """Test CircuitState enum values."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"

    def test_circuit_state_members(self) -> None:
        """Test CircuitState enum members."""
        assert len(CircuitState) == 3
        assert CircuitState.CLOSED in CircuitState
        assert CircuitState.OPEN in CircuitState
        assert CircuitState.HALF_OPEN in CircuitState


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_circuit_breaker_creation_default(self) -> None:
        """Test CircuitBreaker creation with default config."""
        cb = CircuitBreaker()

        assert cb._config is not None
        assert cb._config.failure_threshold == 5
        assert cb._hosts == {}

    def test_circuit_breaker_creation_custom_config(self) -> None:
        """Test CircuitBreaker creation with custom config."""
        config = CircuitBreakerConfig(failure_threshold=10)
        cb = CircuitBreaker(config=config)

        assert cb._config.failure_threshold == 10

    @pytest.mark.asyncio
    async def test_can_proceed_new_host(self) -> None:
        """Test can_proceed for new host (should create state and allow)."""
        cb = CircuitBreaker()

        result = await cb.can_proceed("example.com")

        assert result is True
        assert "example.com" in cb._hosts
        assert cb._hosts["example.com"].state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_can_proceed_closed_state(self) -> None:
        """Test can_proceed when circuit is CLOSED."""
        cb = CircuitBreaker()
        cb._hosts["example.com"] = HostState(state=CircuitState.CLOSED)

        result = await cb.can_proceed("example.com")

        assert result is True

    @pytest.mark.asyncio
    async def test_can_proceed_open_state_within_timeout(self) -> None:
        """Test can_proceed when circuit is OPEN within timeout."""
        cb = CircuitBreaker()
        cb._hosts["example.com"] = HostState(
            state=CircuitState.OPEN,
            last_failure_time=9999999999.0,  # Far future time
        )

        result = await cb.can_proceed("example.com")

        assert result is False

    @pytest.mark.asyncio
    async def test_can_proceed_open_state_after_timeout(self) -> None:
        """Test can_proceed when circuit is OPEN after timeout (should transition to HALF_OPEN)."""
        cb = CircuitBreakerConfig(timeout=0.1)
        circuit_breaker = CircuitBreaker(cb)
        circuit_breaker._hosts["example.com"] = HostState(
            state=CircuitState.OPEN,
            last_failure_time=0.0,  # Past time
        )

        result = await circuit_breaker.can_proceed("example.com")

        assert result is True
        assert circuit_breaker._hosts["example.com"].state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_can_proceed_half_open_within_limit(self) -> None:
        """Test can_proceed when circuit is HALF_OPEN within call limit."""
        config = CircuitBreakerConfig(half_open_max_calls=3)
        cb = CircuitBreaker(config)
        cb._hosts["example.com"] = HostState(
            state=CircuitState.HALF_OPEN,
            half_open_calls=1,
        )

        result = await cb.can_proceed("example.com")

        assert result is True
        assert cb._hosts["example.com"].half_open_calls == 2

    @pytest.mark.asyncio
    async def test_can_proceed_half_open_at_limit(self) -> None:
        """Test can_proceed when circuit is HALF_OPEN at call limit."""
        config = CircuitBreakerConfig(half_open_max_calls=3)
        cb = CircuitBreaker(config)
        cb._hosts["example.com"] = HostState(
            state=CircuitState.HALF_OPEN,
            half_open_calls=3,
        )

        result = await cb.can_proceed("example.com")

        assert result is False

    @pytest.mark.asyncio
    async def test_record_success_closed_state(self) -> None:
        """Test record_success when circuit is CLOSED."""
        cb = CircuitBreaker()
        cb._hosts["example.com"] = HostState(
            state=CircuitState.CLOSED,
            failure_count=3,
        )

        await cb.record_success("example.com")

        assert cb._hosts["example.com"].failure_count == 0

    @pytest.mark.asyncio
    async def test_record_success_half_open_below_threshold(self) -> None:
        """Test record_success in HALF_OPEN below success threshold."""
        config = CircuitBreakerConfig(success_threshold=2)
        cb = CircuitBreaker(config)
        cb._hosts["example.com"] = HostState(
            state=CircuitState.HALF_OPEN,
            success_count=0,
        )

        await cb.record_success("example.com")

        assert cb._hosts["example.com"].success_count == 1
        assert cb._hosts["example.com"].state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_record_success_half_open_at_threshold(self) -> None:
        """Test record_success in HALF_OPEN reaching success threshold (should transition to CLOSED)."""
        config = CircuitBreakerConfig(success_threshold=2)
        cb = CircuitBreaker(config)
        cb._hosts["example.com"] = HostState(
            state=CircuitState.HALF_OPEN,
            success_count=1,
        )

        await cb.record_success("example.com")

        assert cb._hosts["example.com"].state == CircuitState.CLOSED
        assert cb._hosts["example.com"].failure_count == 0
        assert cb._hosts["example.com"].success_count == 0

    @pytest.mark.asyncio
    async def test_record_success_unknown_host(self) -> None:
        """Test record_success for unknown host (should do nothing)."""
        cb = CircuitBreaker()

        # Should not raise error
        await cb.record_success("unknown.com")

        assert "unknown.com" not in cb._hosts

    @pytest.mark.asyncio
    async def test_record_failure_new_host(self) -> None:
        """Test record_failure for new host."""
        cb = CircuitBreaker()

        await cb.record_failure("example.com")

        assert "example.com" in cb._hosts
        assert cb._hosts["example.com"].failure_count == 1

    @pytest.mark.asyncio
    async def test_record_failure_closed_below_threshold(self) -> None:
        """Test record_failure in CLOSED below failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=5)
        cb = CircuitBreaker(config)
        cb._hosts["example.com"] = HostState(
            state=CircuitState.CLOSED,
            failure_count=2,
        )

        await cb.record_failure("example.com")

        assert cb._hosts["example.com"].failure_count == 3
        assert cb._hosts["example.com"].state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_record_failure_closed_at_threshold(self) -> None:
        """Test record_failure in CLOSED reaching failure threshold (should transition to OPEN)."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config)
        cb._hosts["example.com"] = HostState(
            state=CircuitState.CLOSED,
            failure_count=2,
        )

        await cb.record_failure("example.com")

        assert cb._hosts["example.com"].state == CircuitState.OPEN
        assert cb._hosts["example.com"].failure_count == 3

    @pytest.mark.asyncio
    async def test_record_failure_half_open(self) -> None:
        """Test record_failure in HALF_OPEN (should transition to OPEN)."""
        cb = CircuitBreaker()
        cb._hosts["example.com"] = HostState(
            state=CircuitState.HALF_OPEN,
            half_open_calls=2,
        )

        await cb.record_failure("example.com")

        assert cb._hosts["example.com"].state == CircuitState.OPEN
        assert cb._hosts["example.com"].half_open_calls == 0

    def test_get_state_existing_host(self) -> None:
        """Test get_state for existing host."""
        cb = CircuitBreaker()
        cb._hosts["example.com"] = HostState(state=CircuitState.OPEN)

        result = cb.get_state("example.com")

        assert result == CircuitState.OPEN

    def test_get_state_unknown_host(self) -> None:
        """Test get_state for unknown host."""
        cb = CircuitBreaker()

        result = cb.get_state("unknown.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_full_circuit_breaker_cycle(self) -> None:
        """Test full circuit breaker cycle: CLOSED -> OPEN -> HALF_OPEN -> CLOSED."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=1,
            timeout=0.1,
        )
        cb = CircuitBreaker(config)

        host = "example.com"

        # Start in CLOSED state
        assert await cb.can_proceed(host)

        # Record failures to trigger OPEN
        await cb.record_failure(host)
        await cb.record_failure(host)

        # Should be OPEN now
        assert cb.get_state(host) == CircuitState.OPEN
        assert not await cb.can_proceed(host)

        # Wait for timeout
        await asyncio.sleep(0.15)

        # Should transition to HALF_OPEN and allow request
        assert await cb.can_proceed(host)
        assert cb.get_state(host) == CircuitState.HALF_OPEN

        # Record success to transition back to CLOSED
        await cb.record_success(host)

        # Should be CLOSED again
        assert cb.get_state(host) == CircuitState.CLOSED
