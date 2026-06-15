"""
WebSocket with auto-reconnect example.

If the connection drops the client will retry up to 5 times
with exponential backoff.

Usage:
    python examples/websocket/reconnect.py
"""
from fasthttp import FastHTTP, WebSocket

app = FastHTTP()


@app.ws(url="wss://echo.websocket.org", reconnect=True, max_retries=5)
async def persistent(ws: WebSocket) -> None:
    async for msg in ws:
        print(f"Echo: {msg}")


if __name__ == "__main__":
    app.run()
