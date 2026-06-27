"""
SSE client — Wikimedia recent changes stream.

Connects to Wikimedia EventStreams (free, no auth) and prints
recent wiki edits as they happen.

Usage:
    python examples/sse/basic.py
"""
import json

from fasthttp import FastHTTP, SSEEvent

app = FastHTTP()


@app.sse(url="https://stream.wikimedia.org/v2/stream/recentchange")
async def watch_wikipedia(event: SSEEvent) -> None:
    try:
        data = json.loads(event.data)
        title = data.get("title", "?")
        user = data.get("user", "?")
        print(f"[{event.event}] {title} — edited by {user}")
    except json.JSONDecodeError:
        print(f"[{event.event}] {event.data}")


if __name__ == "__main__":
    app.run()
