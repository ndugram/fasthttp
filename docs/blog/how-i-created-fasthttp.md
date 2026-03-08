---
title: How I Created My Own HTTP Library
description: The story of how an idea in September 2025 turned into a real project
date: 2025-09-01
---

# How I Created fasthttp-client

Back in September 2025, I stumbled upon FastAPI and just couldn't believe it. Like, really — check out this code:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello!"}
```

And it just works. No bs, simple and clear. I was totally hooked — how can you make everything work through a decorator and everything happens automatically under the hood?

Then in December, I started diving deep into how this framework works internally. How it generates OpenAPI docs, how it handles async requests, how Pydantic integrates right into the endpoints. The deeper I dug, the more I realized — there's massive architectural work behind this simplicity.

## Why Not a Framework

First I thought: "Yo, let me build something like this too, like a web framework." But then I calculated — you gotta know so much stuff: HTTP/1.1, HTTP/2, HTTP/3, ASGI/WSGI, event loops, routing, validation... That takes years of experience. There's no way I could handle such a project solo.

So the idea of creating a web framework just faded away.

## Then This YouTube Video Happened

That same evening I'm watching YouTube, and I see a video — comparing speed of requests, aiohttp and httpx. They show benchmarks, graphs, numbers. And I'm like: yo, I can make my own HTTP client! Not just another wrapper around aiohttp, but something of my own with a proper API.

Wanted to make a library that would:
- Be simple like requests
- Support async like aiohttp
- Have beautiful logs, not through print()
- And pydantic should work right away without any extra work

## Started Coding at Night

Sat down in the evening, started coding. First made a wrapper around aiohttp — just wanted to test if the idea works at all. Then switched to httpx because it's more stable and convenient. And then gradually added features:

- Made beautiful logging
- Hooked up Pydantic validation
- Built Fluent API
- Added middlewares
- Connected HTTP/2 through hyper-h2

And it works. Honestly, didn't expect it to turn out like this.

## What the Library Can Do

As I was coding, I kept adding feature after feature. Initially just wanted to make a convenient wrapper, but then realized — I can do much more. Here's what came out:

**Declarative style** — no bs with creating sessions and manual context management. Just a decorator and the request is ready:

```python
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://api.github.com/users/ndugram")
async def get_user(resp):
    return resp.json()
```

**Async and parallel** — everything runs on [httpx](https://www.python-httpx.org/) and asyncio. If you have 10 requests, they run in parallel, not one by one. This really saves time, especially when working with a bunch of APIs.

**Dependencies** — you can modify any request before sending. Add auth token, headers, logging — everything through Depends. Exactly like in FastAPI:

```python
from fasthttp import FastHTTP, Depends

app = FastHTTP()

async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config

@app.get(url="https://api.example.com/data", dependencies=[Depends(add_auth)])
async def protected(resp):
    return resp.json()
```

**Middleware** — global logic for all requests. Caching, logging, retries — anything you want. There's even a ready-made [CacheMiddleware](https://fasthttp.readthedocs.io/en/middleware.html#cache) that caches responses.

**Pydantic validation** — responses are automatically validated through Pydantic models. No manual checks needed:

```python
from pydantic import BaseModel
from fasthttp import FastHTTP

app = FastHTTP()

class User(BaseModel):
    login: str
    id: int
    html_url: str

@app.get(url="https://api.github.com/users/ndugram", response_model=User)
async def get_user(resp):
    return resp.json()
```

**Security out of the box** — this is a whole separate thing. The library includes:
- SSRF protection (blocking localhost and private IPs)
- Circuit breaker — if a server is down, requests don't fly into the void
- Secret masking in logs (tokens, passwords — everything hidden)
- Response size limits
- Dangerous redirect protection
- Timeouts

All of this is enabled with one line `security=True` (enabled by default).

**HTTP/2** — modern protocol support via [hyper-h2](https://hyper-h2.readthedocs.io/). Enabled like this: `app = FastHTTP(http2=True)`.

**CLI** — you can run requests right from the terminal without writing Python code. Convenient for API testing.

**Beautiful logging** — instead of boring `print("GET", url)` you get nice colored logs with execution time, status code and more:

```
FastHTTP started
Sending 3 requests
→ GET https://api.github.com/users/ndugram | headers={...}
✔️ GET    https://api.github.com/users/ndugram  200  145.23ms
Done in 0.23s
```

I built all of this because I really needed it myself. At work I was constantly hitting different APIs, writing the same thing over and over. And I thought — why isn't there a normal tool for this?

## About the Team

I want to say separately — I'm not doing this alone. There are people who actively contribute to the project, help with code, fix bugs, write documentation. Without them, the library would be much worse. Special thanks to:

- Those who open Issues with bugs — this really helps
- Those who make Pull Requests — you guys are the best
- Those who just drop stars and give feedback

You motivate me to keep developing the project. It's not just "my project" — it's our project.

## Proud of the Project

Now looking at what came out — and I understand it was the right decision. fasthttp-client is not just another library for requests. It's my contribution to the Python ecosystem, my vision of what a convenient API should look like.

Maybe someone will say "why another HTTP client". But I think the project has a future. At least, I'll keep developing it.

---

**Want to try it?** Check out the [Quick Start](../en/quick-start.md) or look at [Examples](../en/examples.md). I'd love it if you check out [GitHub](https://github.com/ndugram/fasthttp) and drop a star 😄

**Useful links:**
- [PyPI](https://pypi.org/project/fasthttp-client/) — download the library
- [GitHub Issues](https://github.com/ndugram/fasthttp/issues) — report a bug
- [Telegram chat](https://t.me/fasthttp_chat) — ask a question (if you have one)
