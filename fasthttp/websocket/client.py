from __future__ import annotations

from typing import TYPE_CHECKING, Any

import orjson

from .exceptions import WebSocketConnectionError, WebSocketError

if TYPE_CHECKING:
    import logging

    from websockets import WebSocketClientProtocol


class WebSocketMessage:
    """
    A single WebSocket message received from the server.

    Provides convenient access to the underlying data as text, bytes,
    or parsed JSON.
    """

    __slots__ = ("_data",)

    def __init__(self, data: str | bytes) -> None:
        self._data = data

    @property
    def text(self) -> str | None:
        """The message as a string, or None if the message is binary."""
        return self._data if isinstance(self._data, str) else None  # type: ignore[return-value]

    @property
    def data(self) -> str | bytes:
        """The raw underlying message data (str or bytes)."""
        return self._data

    def json(self) -> Any:  # noqa: ANN401
        """Parse the message body as JSON using orjson."""
        if isinstance(self._data, bytes):
            return orjson.loads(self._data)
        return orjson.loads(self._data)

    def __str__(self) -> str:
        return str(self._data)


class WebSocket:
    """
    WebSocket connection wrapper for fasthttp.

    Wraps a ``websockets`` client connection and provides a
    fasthttp-native async interface for sending and receiving messages.

    Usage:
        .. code-block:: python

            websocket = WebSocket(connection, logger)
            await websocket.send("Hello")
            msg = await websocket.recv()
            print(msg.text)
    """

    def __init__(
        self,
        connection: WebSocketClientProtocol,
        logger: logging.Logger,
    ) -> None:
        self._conn = connection
        self._logger = logger

    @property
    def closed(self) -> bool:
        """Whether the WebSocket connection has been closed."""
        return self._conn.closed

    @property
    def local_address(self) -> tuple[str, int] | None:
        """The local endpoint of the connection."""
        return self._conn.local_address  # type: ignore[no-any-return]

    @property
    def remote_address(self) -> tuple[str, int] | None:
        """The remote endpoint of the connection."""
        return self._conn.remote_address  # type: ignore[no-any-return]

    async def send(self, data: str | bytes | dict | list) -> None:
        """
        Send a message.

        ``dict`` and ``list`` values are automatically serialised
        to a JSON string before sending.
        """
        if isinstance(data, (dict, list)):
            data = orjson.dumps(data).decode()
        await self._conn.send(data)

    async def send_str(self, data: str) -> None:
        """Send a text (UTF-8) message."""
        await self._conn.send(data)

    async def send_bytes(self, data: bytes) -> None:
        """Send a binary message."""
        await self._conn.send(data)

    async def recv(self) -> WebSocketMessage:
        """Receive a single message from the server."""
        try:
            data = await self._conn.recv()
            return WebSocketMessage(data)
        except Exception as exc:
            msg = f"Connection closed while receiving: {exc}"
            raise WebSocketConnectionError(msg) from exc

    async def recv_str(self) -> str:
        """
        Receive a text message.

        Raises ``TypeError`` when the received message is binary.
        """
        data = await self._conn.recv()
        if isinstance(data, bytes):
            msg = "Received binary data, expected text"
            raise TypeError(msg)
        return data

    async def recv_bytes(self) -> bytes:
        """
        Receive a binary message.

        Raises ``TypeError`` when the received message is text.
        """
        data = await self._conn.recv()
        if isinstance(data, str):
            msg = "Received text data, expected binary"
            raise TypeError(msg)
        return data

    async def close(self, code: int = 1000, reason: str = "") -> None:
        """Gracefully close the WebSocket connection."""
        await self._conn.close(code=code, reason=reason)
        self._logger.debug("WebSocket closed: code=%d reason=%s", code, reason)

    async def ping(self, data: bytes | None = None) -> None:
        """Send a WebSocket ping frame."""
        await self._conn.ping(data)

    async def pong(self, data: bytes | None = None) -> None:
        """Send a WebSocket pong frame."""
        await self._conn.pong(data)

    # -- async iteration -------------------------------------------------------

    def __aiter__(self) -> WebSocket:
        return self

    async def __anext__(self) -> WebSocketMessage:
        try:
            data = await self._conn.recv()
            return WebSocketMessage(data)
        except WebSocketError:
            raise StopAsyncIteration from None
        except Exception:  # noqa: BLE001
            raise StopAsyncIteration from None
