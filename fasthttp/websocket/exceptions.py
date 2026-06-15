class WebSocketError(Exception):
    """Base exception for WebSocket-related errors."""


class WebSocketConnectionError(WebSocketError):
    """Raised when the WebSocket connection is closed unexpectedly."""
