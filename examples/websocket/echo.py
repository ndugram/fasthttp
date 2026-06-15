"""
WebSocket echo client example.

Connects to a public WebSocket echo server, sends a message,
and prints the response.

Usage:
    python examples/websocket/echo.py
"""
from fasthttp import FastHTTP, WebSocket

app = FastHTTP()


@app.ws(url="wss://echo.websocket.org")
async def echo(ws: WebSocket) -> None:
    await ws.send("Hello from fasthttp!")
    msg = await ws.recv()
    print(f"Received: {msg}")


if __name__ == "__main__":
    app.run()
