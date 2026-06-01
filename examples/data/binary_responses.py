"""
Examples for response.bytes(), response.html(), response.xml().

Real endpoints used:
  bytes() → https://httpbin.org/image/png    (PNG image)
  html()  → https://example.com              (plain HTML page)
  xml()   → https://httpbin.org/xml          (XML document)
"""

from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


# --- bytes() ---


@app.get(url="https://httpbin.org/image/png")
async def download_png(resp: Response) -> dict:
    raw = resp.bytes()
    return {
        "size_bytes": len(raw),
        "is_png": raw[:4] == b"\x89PNG",
        "content_type": resp.headers.get("content-type"),
    }


@app.get(url="https://httpbin.org/bytes/32")
async def download_random_bytes(resp: Response) -> dict:
    raw = resp.bytes()
    return {"size_bytes": len(raw), "hex_preview": raw[:8].hex()}


# --- html() ---


@app.get(url="https://example.com")
async def get_html_page(resp: Response) -> dict:
    html = resp.html()
    return {
        "length": len(html),
        "starts_with_doctype": html.strip().lower().startswith("<!doctype"),
        "content_type": resp.headers.get("content-type"),
    }


# --- xml() ---


@app.get(url="https://httpbin.org/xml")
async def get_xml(resp: Response) -> dict:
    root = resp.xml()
    return {
        "root_tag": root.tag,
        "children_count": len(root),
        "content_type": resp.headers.get("content-type"),
    }


@app.get(url="https://feeds.bbci.co.uk/news/rss.xml")
async def get_bbc_rss(resp: Response) -> dict:
    root = resp.xml()
    channel = root.find("channel")
    if channel is None:
        return {"error": "no channel element"}
    items = channel.findall("item")
    titles = [item.findtext("title") for item in items[:5]]
    return {
        "feed_title": channel.findtext("title"),
        "item_count": len(items),
        "latest_titles": titles,
    }


if __name__ == "__main__":
    app.run()
