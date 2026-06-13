from __future__ import annotations

import asyncio
import logging
from contextvars import ContextVar
from typing import TYPE_CHECKING, Annotated, Any, ClassVar

from annotated_doc import Doc

from .base import BaseMiddleware

if TYPE_CHECKING:
    from fasthttp.response import Response
    from fasthttp.routing import Route
    from fasthttp.types import RequestsOptinal

_retry_state: ContextVar[dict[str, Any] | None] = ContextVar(
    "retry_state", default=None
)

logger = logging.getLogger("fasthttp")


class RetryMiddleware(BaseMiddleware):
    """
    Middleware for automatic request retries with exponential backoff.

    Retries requests that fail due to connection errors, timeouts,
    or specific HTTP status codes (429, 5xx).

    Example:
        ```python
        from fasthttp import FastHTTP
        from fasthttp.middleware import RetryMiddleware

        app = FastHTTP(
            middleware=RetryMiddleware(
                max_retries=3,
                retry_on={429, 500, 502, 503, 504},
                backoff_factor=0.5,
            )
        )

        @app.get("https://api.example.com/data")
        async def get_data(resp: Response):
            return resp.json()

        app.run()
        ```
    """

    __priority__: ClassVar[int] = 1000
    __methods__: ClassVar[None] = None
    __enabled__: ClassVar[bool] = True

    def __init__(
        self,
        max_retries: Annotated[
            int,
            Doc("Maximum number of retry attempts. Default 3."),
        ] = 3,
        retry_on: Annotated[
            set[int] | None,
            Doc(
                "HTTP status codes that trigger a retry. "
                "Default {429, 500, 502, 503, 504}."
            ),
        ] = None,
        backoff_factor: Annotated[
            float,
            Doc(
                "Multiplier for exponential backoff delay. "
                "Delay = backoff_factor * 2^attempt. Default 0.5."
            ),
        ] = 0.5,
        max_delay: Annotated[
            float,
            Doc("Maximum delay between retries in seconds. Default 30.0."),
        ] = 30.0,
        retry_exceptions: Annotated[
            tuple[type[Exception], ...] | None,
            Doc(
                "Exception types that trigger a retry. "
                "Default (ConnectError, TimeoutException)."
            ),
        ] = None,
    ) -> None:
        self.max_retries = max_retries
        self.retry_on = retry_on or {429, 500, 502, 503, 504}
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.retry_exceptions = retry_exceptions or (
            Exception,
        )

    def _should_retry_status(self, status_code: int) -> bool:
        return status_code in self.retry_on

    def _should_retry_exception(self, exc: Exception) -> bool:
        return isinstance(exc, self.retry_exceptions)

    def _calculate_delay(self, attempt: int, response: Response | None) -> float:
        if response is not None:
            retry_after = response.headers.get("retry-after")
            if retry_after:
                try:
                    return min(float(retry_after), self.max_delay)
                except (ValueError, TypeError):
                    pass

        delay = self.backoff_factor * (2**attempt)
        return min(delay, self.max_delay)

    async def request(
        self,
        method: str,  # noqa: ARG002
        url: str,  # noqa: ARG002
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        state = _retry_state.get()
        if state is None:
            _retry_state.set({"attempt": 0, "max": self.max_retries})
        return kwargs

    async def response(self, response: Response) -> Response:
        state = _retry_state.get()
        if state is None:
            return response

        attempt = state.get("attempt", 0)
        max_retries = state.get("max", self.max_retries)
        if self._should_retry_status(response.status) and attempt < max_retries:
            state["attempt"] = attempt + 1
            _retry_state.set(state)

            delay = self._calculate_delay(attempt, response)
            logger.debug(
                "Retry %d/%d after %.2fs (status %d)",
                attempt + 1,
                max_retries,
                delay,
                response.status,
            )
            await asyncio.sleep(delay)

            raise RetrySignal(str(response.status))

        _retry_state.set(None)
        return response

    async def on_error(
        self,
        error: Exception,
        route: Route,  # noqa: ARG002
        config: RequestsOptinal,  # noqa: ARG002
    ) -> None:
        state = _retry_state.get()
        if state is None:
            return

        attempt = state.get("attempt", 0)
        max_retries = state.get("max", self.max_retries)
        if self._should_retry_exception(error) and attempt < max_retries:
            state["attempt"] = attempt + 1
            _retry_state.set(state)

            delay = self._calculate_delay(attempt, None)
            logger.debug(
                "Retry %d/%d after %.2fs (error: %s)",
                attempt + 1,
                max_retries,
                delay,
                type(error).__name__,
            )
            await asyncio.sleep(delay)

            raise RetrySignal(str(error)) from error


class RetrySignal(Exception):  # noqa: N818
    """Internal signal raised to trigger a retry in the client."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Retry: {reason}")
