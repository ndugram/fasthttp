---
title: How I Created My Own HTTP Library
description: The story of how an idea in September 2025 turned into a real project
date: 2025-09-01
---

# Who Am I

My name is **NEFOR**. I'm a web developer and have been working with **Python frameworks for about 2 years**, mainly with **FastAPI** and **Django**.

I've always been interested not just in writing code, but in **understanding how tools work under the hood**: how frameworks are built, how HTTP requests are processed, and how library architecture is designed.

It was exactly this interest that eventually led to my own open-source project. By the way, about open-source — I was completely inspired by FastAPI. I saw how Sebastián Ramírez created a cool project that actually helps people, and I thought: why shouldn't I do something similar? Not on that scale of course, but still.

# How I Created fasthttp-client

Back in September 2025, I stumbled upon FastAPI and just couldn't believe it. Like, really — you write a decorator over a function and it's already a working endpoint. No bs, simple and clear. I was totally hooked — how can you make everything work through a decorator and everything happens automatically under the hood?

Then in December, I started diving deep into how this framework works internally. How it generates OpenAPI docs, how it handles async requests, how Pydantic integrates right into the endpoints. The deeper I dug, the more I realized — there's massive architectural work behind this simplicity.

## Why Not a Framework

First I thought: "Yo, let me build something like this too, like a web framework." But then I calculated — you gotta know so much stuff: HTTP/1.1, HTTP/2, HTTP/3, ASGI/WSGI, event loops, routing, validation... That takes years of experience. There's no way I could handle such a project solo.

So the idea of creating a web framework just faded away.

## Then This YouTube Video Happened

That same evening I'm watching YouTube, and I see a video — comparing speed of requests, aiohttp and httpx. They show benchmarks, graphs, numbers. And I'm like: yo, I can make my own HTTP client! Not just another wrapper around aiohttp, but something of my own with a proper API.

Wanted to make a library that would be simple like requests, support async like aiohttp, have beautiful logs not through print(), and pydantic should work right away without any extra work.

## Started Coding at Night

Sat down in the evening, started coding. First made a wrapper around aiohttp — just wanted to test if the idea works at all. But then I realized aiohttp wasn't for me.

First, aiohttp lets you run your own server, and I didn't need that. I wanted to add Swagger documentation to the project like in FastAPI — attempts were good but pathetic. Couldn't integrate it properly.

Second, I decided to add HTTP/2 support. And turns out aiohttp doesn't support it. Had to completely switch to httpx.

It was a tough decision — rewriting everything from scratch. But httpx turned out more stable and convenient, plus HTTP/2 out of the box through hyper-h2. So in the end — right choice.

Then gradually added features: beautiful logging, Pydantic validation, Fluent API, middlewares, security. And it works. Honestly, didn't expect it to turn out like this.

## Code Challenges

One of the main problems was making the code readable. I wanted other developers to easily understand the project, get the architecture, and contribute. It's not as simple as it seems — writing code for yourself and writing code for others are different things.

Had to constantly refactor, rewrite chunks, think about naming and structure. But now I can confidently say — there's clean code in the project. At least, that's what I aimed for.

## What the Library Can Do

As I was coding, I kept adding feature after feature. Initially just wanted to make a convenient wrapper, but then realized — I can do much more.

**Declarative style** — no bs with creating sessions and manual context management. Just a decorator and the request is ready.

**Async and parallel** — everything runs on httpx and asyncio. If you have 10 requests, they run in parallel, not one by one. This really saves time, especially when working with a bunch of APIs.

**Dependencies** — you can modify any request before sending. Add auth token, headers, logging — everything through Depends. Exactly like in FastAPI.

**Middleware** — global logic for all requests. Caching, logging, retries — anything you want. There's even a ready-made CacheMiddleware that caches responses.

**Pydantic validation** — responses are automatically validated through Pydantic models. No manual checks needed.

**Security out of the box** — this is a whole separate thing. The library includes SSRF protection, circuit breaker, secret masking in logs, response size limits, dangerous redirect protection, and timeouts. All of this is enabled with one line.

**HTTP/2** — modern protocol support via hyper-h2.

**CLI** — you can run requests right from the terminal without writing Python code. Convenient for API testing.

**Beautiful logging** — instead of boring print() you get nice colored logs with execution time, status code and more.

I built all of this because I really needed it myself. At work I was constantly hitting different APIs, writing the same thing over and over. And I thought — why isn't there a normal tool for this?

## What People Say

There are people who've already tried the library. And you know what? They say it looks really really cool. No one's seen this before — an HTTP client with a declarative approach like in FastAPI.

Some even write that I'm a genius. Of course, that's an exaggeration, but it's nice to hear. When people appreciate your work — it motivates you to continue.

## About the Team

I want to say separately — I'm not doing this alone. There are people who actively contribute to the project, help with code, fix bugs, write documentation. Without them, the library would be much worse.

But not everything is smooth. There are conflicts. Some people propose very dumb ideas that I don't want to add to the project. Have to explain why it won't work, argue, stand my ground. It's normal for open-source — everyone has their own opinion.

But overall I'm grateful to everyone who works on the project behind the scenes — proposes ideas, helps with code, writes documentation. Special thanks to those who open Issues with bugs, make Pull Requests, drop stars and give feedback.

You motivate me to keep developing the project. It's not just "my project" — it's our project.

## What's Next

Honestly, I can't say what specific plans I have for the future. Many ideas come at the most inconvenient moment — when you're showering, riding the subway, or trying to fall asleep. So it's hard to predict what will be added in advance.

But one thing I can say for sure — the project will continue to develop. I'll be adding new features, improving existing ones, listening to user feedback. So stay tuned for updates.

## Proud of the Project

Now looking at what came out — and I understand it was the right decision. fasthttp-client is not just another library for requests. It's my contribution to the Python ecosystem, my vision of what a convenient API should look like.

Maybe someone will say "why another HTTP client". But I think the project has a future. At least, I'll keep developing it.

---

**Want to try it?** Check out the [Quick Start](../en/quick-start.md) or look at [Examples](../en/examples.md). I'd love it if you check out [GitHub](https://github.com/ndugram/fasthttp) and drop a star 😄

**Useful links:**
- [PyPI](https://pypi.org/project/fasthttp-client/) — download the library
- [GitHub Issues](https://github.com/ndugram/fasthttp/issues) — report a bug
- [Telegram chat](https://t.me/fasthttp_chat) — ask a question (if you have one)
