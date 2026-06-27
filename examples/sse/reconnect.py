"""
SSE with auto-reconnect and custom headers.

Connects to an SSE endpoint with an auth token and automatically
reconnects up to 10 times if the connection drops.

Usage:
    python examples/sse/reconnect.py
"""
import json

from fasthttp import FastHTTP, SSEEvent

app = FastHTTP()


@app.sse(
    url="https://stream.wikimedia.org/v2/stream/recentchange",
    headers={"User-Agent": "FastHTTP-SSE/1.0"},
    reconnect=True,
    max_retries=10,
)
async def watch_wikipedia(event: SSEEvent) -> None:
    data = json.loads(event.data)
    print(f"[{event.event}] {data.get('title', '?')}")


if __name__ == "__main__":
    app.run()
