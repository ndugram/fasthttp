"""
WebSocket stream example — reads messages with ``async for``.

This example connects to the Binance public trade stream for
BTC/USDT and prints each trade as it arrives.  Press Ctrl+C
to stop.

Usage:
    python examples/websocket/stream.py
"""
from fasthttp import FastHTTP, WebSocket

app = FastHTTP()


@app.ws(url="wss://stream.binance.com:9443/ws/btcusdt@trade")
async def trades(ws: WebSocket) -> None:
    async for msg in ws:
        data = msg.json()
        price = data.get("p", "?")
        qty = data.get("q", "?")
        print(f"BTC/USDT — price: {price}, qty: {qty}")


if __name__ == "__main__":
    app.run()
