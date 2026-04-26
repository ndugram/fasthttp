"""Comprehensive tests for fasthttp middleware system."""
import asyncio
import time
from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock

import pytest

from fasthttp.middleware import (
    BaseMiddleware,
    CacheEntry,
    CacheMiddleware,
    MiddlewareChain,
    MiddlewareManager,
)
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.types import HTTPMethod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_route(
    method: str = "GET",
    url: str = "https://example.com/api",
    params: dict | None = None,
) -> Route:
    async def handler(resp: Response) -> Response:
        return resp

    return Route(method=method, url=url, handler=handler, params=params)


def make_response(status: int = 200, text: str = "ok") -> Response:
    return Response(status=status, text=text, headers={}, method="GET")


class SimpleMiddleware(BaseMiddleware):
    __return_type__: ClassVar = None
    __priority__: ClassVar[int] = 0
    __methods__: ClassVar[list[HTTPMethod] | None] = None
    __enabled__: ClassVar[bool] = True

    def __init__(self, name: str = "simple") -> None:
        self.name = name
        self.requests: list[str] = []
        self.responses: list[int] = []
        self.errors: list[str] = []

    async def request(self, method, url, kwargs):
        self.requests.append(f"{method}:{url}")
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"][f"X-{self.name}"] = "1"
        return kwargs

    async def response(self, response):
        self.responses.append(response.status)
        return response

    async def on_error(self, error, route, config):
        self.errors.append(type(error).__name__)


class PriorityMiddleware(BaseMiddleware):
    __return_type__: ClassVar = None
    __methods__: ClassVar[list[HTTPMethod] | None] = None
    __enabled__: ClassVar[bool] = True

    def __init__(self, priority: int, order_log: list) -> None:
        self.__priority__ = priority
        self._order = order_log

    async def request(self, method, url, kwargs):
        self._order.append(f"req:{self.__priority__}")
        return kwargs

    async def response(self, response):
        self._order.append(f"res:{self.__priority__}")
        return response


# ---------------------------------------------------------------------------
# BaseMiddleware
# ---------------------------------------------------------------------------

class TestBaseMiddleware:
    def test_repr_with_return_type(self):
        class Mw(BaseMiddleware):
            __return_type__ = bool
            __priority__ = 0
            __methods__ = None
            __enabled__ = True

        assert repr(Mw()) == "<Mw return_type=<class 'bool'>>"

    def test_repr_without_return_type(self):
        mw = SimpleMiddleware()
        assert "SimpleMiddleware" in repr(mw)
        assert "return_type=None" in repr(mw)

    def test_or_returns_middleware_chain(self):
        a = SimpleMiddleware("a")
        b = SimpleMiddleware("b")
        chain = a | b
        assert isinstance(chain, MiddlewareChain)
        assert len(chain) == 2

    def test_or_chaining_three(self):
        a = SimpleMiddleware("a")
        b = SimpleMiddleware("b")
        c = SimpleMiddleware("c")
        chain = a | b | c
        assert len(chain) == 3

    @pytest.mark.asyncio
    async def test_default_request_returns_kwargs(self):
        mw = BaseMiddleware()
        kwargs = {"headers": {"X-Test": "1"}}
        result = await mw.request("GET", "https://example.com", kwargs)
        assert result is kwargs

    @pytest.mark.asyncio
    async def test_default_response_returns_response(self):
        mw = BaseMiddleware()
        resp = make_response()
        result = await mw.response(resp)
        assert result is resp

    @pytest.mark.asyncio
    async def test_default_on_error_returns_none(self):
        mw = BaseMiddleware()
        route = make_route()
        result = await mw.on_error(ValueError("boom"), route, {})
        assert result is None

    def test_init_subclass_called(self):
        called = []

        class Base(BaseMiddleware):
            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                called.append(cls.__name__)

        class Child(Base):
            pass

        assert "Child" in called

    def test_class_attrs_annotations(self):
        annotations = BaseMiddleware.__annotations__
        assert "__return_type__" in annotations
        assert "__priority__" in annotations
        assert "__methods__" in annotations
        assert "__enabled__" in annotations

    def test_class_var_in_annotations(self):
        ann = str(BaseMiddleware.__annotations__["__methods__"])
        assert "ClassVar" in ann
        assert "HTTPMethod" in ann


# ---------------------------------------------------------------------------
# MiddlewareChain
# ---------------------------------------------------------------------------

class TestMiddlewareChain:
    def test_len(self):
        chain = MiddlewareChain([SimpleMiddleware("a"), SimpleMiddleware("b")])
        assert len(chain) == 2

    def test_iter(self):
        a, b = SimpleMiddleware("a"), SimpleMiddleware("b")
        chain = MiddlewareChain([a, b])
        assert list(chain) == [a, b]

    def test_or_appends(self):
        a = SimpleMiddleware("a")
        b = SimpleMiddleware("b")
        c = SimpleMiddleware("c")
        chain = MiddlewareChain([a, b]) | c
        assert len(chain) == 3
        assert list(chain)[2] is c

    def test_repr(self):
        chain = MiddlewareChain([SimpleMiddleware("a"), SimpleMiddleware("b")])
        r = repr(chain)
        assert "MiddlewareChain" in r
        assert "SimpleMiddleware" in r

    def test_pipe_operator_creates_chain(self):
        a = SimpleMiddleware("a")
        b = SimpleMiddleware("b")
        chain = a | b
        items = list(chain)
        assert items[0] is a
        assert items[1] is b

    def test_pipe_chain_then_pipe_more(self):
        a = SimpleMiddleware("a")
        b = SimpleMiddleware("b")
        c = SimpleMiddleware("c")
        chain = (a | b) | c
        assert len(chain) == 3


# ---------------------------------------------------------------------------
# MiddlewareManager — init
# ---------------------------------------------------------------------------

class TestMiddlewareManagerInit:
    def test_init_none(self):
        mm = MiddlewareManager(None)
        assert mm.middlewares == []

    def test_init_empty_list(self):
        mm = MiddlewareManager([])
        assert mm.middlewares == []

    def test_init_list(self):
        a, b = SimpleMiddleware("a"), SimpleMiddleware("b")
        mm = MiddlewareManager([a, b])
        assert len(mm.middlewares) == 2

    def test_init_chain(self):
        a, b = SimpleMiddleware("a"), SimpleMiddleware("b")
        chain = a | b
        mm = MiddlewareManager(chain)
        assert len(mm.middlewares) == 2
        assert mm.middlewares[0] is a

    def test_default_no_args(self):
        mm = MiddlewareManager()
        assert mm.middlewares == []


# ---------------------------------------------------------------------------
# MiddlewareManager — sorting and filtering
# ---------------------------------------------------------------------------

class TestMiddlewareManagerSortingFiltering:
    def test_sorted_by_priority(self):
        order = []
        low = PriorityMiddleware(0, order)
        high = PriorityMiddleware(10, order)
        mm = MiddlewareManager([high, low])
        sorted_mws = mm._sorted()
        assert sorted_mws[0].__priority__ == 0
        assert sorted_mws[1].__priority__ == 10

    def test_sorted_stable_equal_priority(self):
        a = SimpleMiddleware("a")
        b = SimpleMiddleware("b")
        mm = MiddlewareManager([a, b])
        result = mm._sorted()
        assert result[0] is a
        assert result[1] is b

    def test_active_skips_disabled(self):
        a = SimpleMiddleware("a")
        b = SimpleMiddleware("b")
        b.__enabled__ = False
        mm = MiddlewareManager([a, b])
        active = mm._active(mm._sorted(), "GET")
        assert len(active) == 1
        assert active[0] is a

    def test_active_method_filter_matches(self):
        class PostOnly(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = ["POST"]
            __enabled__ = True

        mm = MiddlewareManager([PostOnly()])
        assert len(mm._active(mm._sorted(), "POST")) == 1
        assert len(mm._active(mm._sorted(), "GET")) == 0

    def test_active_method_filter_case_insensitive(self):
        class GetOnly(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = ["get"]
            __enabled__ = True

        mm = MiddlewareManager([GetOnly()])
        assert len(mm._active(mm._sorted(), "GET")) == 1

    def test_active_none_methods_matches_all(self):
        mm = MiddlewareManager([SimpleMiddleware()])
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            assert len(mm._active(mm._sorted(), method)) == 1

    def test_active_disabled_and_method_filter(self):
        class PostOnly(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = ["POST"]
            __enabled__ = False

        mm = MiddlewareManager([PostOnly()])
        assert mm._active(mm._sorted(), "POST") == []

    def test_runtime_toggle_enabled(self):
        mw = SimpleMiddleware()
        mm = MiddlewareManager([mw])
        assert len(mm._active(mm._sorted(), "GET")) == 1
        mw.__enabled__ = False
        assert len(mm._active(mm._sorted(), "GET")) == 0
        mw.__enabled__ = True
        assert len(mm._active(mm._sorted(), "GET")) == 1


# ---------------------------------------------------------------------------
# MiddlewareManager — process_before_request
# ---------------------------------------------------------------------------

class TestProcessBeforeRequest:
    @pytest.mark.asyncio
    async def test_header_added_by_middleware(self):
        mw = SimpleMiddleware("auth")
        mm = MiddlewareManager([mw])
        route = make_route()
        result = await mm.process_before_request(route, {})
        assert result["headers"]["X-auth"] == "1"

    @pytest.mark.asyncio
    async def test_request_order_matches_priority(self):
        order = []
        mm = MiddlewareManager([
            PriorityMiddleware(10, order),
            PriorityMiddleware(0, order),
        ])
        route = make_route()
        await mm.process_before_request(route, {})
        assert order.index("req:0") < order.index("req:10")

    @pytest.mark.asyncio
    async def test_params_added_from_route(self):
        route = make_route(params={"q": "test"})
        mm = MiddlewareManager([])
        result = await mm.process_before_request(route, {})
        assert result["params"] == {"q": "test"}

    @pytest.mark.asyncio
    async def test_middleware_can_modify_params(self):
        class ParamsMw(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = None
            __enabled__ = True

            async def request(self, method, url, kwargs):
                kwargs["params"] = {"injected": "true"}
                return kwargs

        mm = MiddlewareManager([ParamsMw()])
        route = make_route(params={"original": "1"})
        result = await mm.process_before_request(route, {})
        assert result["params"] == {"injected": "true"}

    @pytest.mark.asyncio
    async def test_disabled_middleware_skipped(self):
        mw = SimpleMiddleware("skipped")
        mw.__enabled__ = False
        mm = MiddlewareManager([mw])
        route = make_route()
        result = await mm.process_before_request(route, {})
        assert "X-skipped" not in (result.get("headers") or {})

    @pytest.mark.asyncio
    async def test_empty_middleware_returns_config(self):
        mm = MiddlewareManager()
        route = make_route()
        config = {"headers": {"X-Existing": "yes"}, "timeout": 10.0}
        result = await mm.process_before_request(route, config)
        assert result["headers"]["X-Existing"] == "yes"

    @pytest.mark.asyncio
    async def test_multiple_middlewares_chain_kwargs(self):
        class Add1(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = None
            __enabled__ = True

            async def request(self, method, url, kwargs):
                kwargs["headers"] = kwargs.get("headers") or {}
                kwargs["headers"]["X-Step"] = "1"
                return kwargs

        class Add2(BaseMiddleware):
            __return_type__ = None
            __priority__ = 1
            __methods__ = None
            __enabled__ = True

            async def request(self, method, url, kwargs):
                kwargs["headers"]["X-Step2"] = "2"
                return kwargs

        mm = MiddlewareManager([Add1(), Add2()])
        route = make_route()
        result = await mm.process_before_request(route, {})
        assert result["headers"]["X-Step"] == "1"
        assert result["headers"]["X-Step2"] == "2"

    @pytest.mark.asyncio
    async def test_method_filtered_middleware_not_called(self):
        class PostOnly(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = ["POST"]
            __enabled__ = True
            called = False

            async def request(self, method, url, kwargs):
                PostOnly.called = True
                return kwargs

        mm = MiddlewareManager([PostOnly()])
        route = make_route(method="GET")
        await mm.process_before_request(route, {})
        assert not PostOnly.called


# ---------------------------------------------------------------------------
# MiddlewareManager — process_after_response
# ---------------------------------------------------------------------------

class TestProcessAfterResponse:
    @pytest.mark.asyncio
    async def test_response_called_in_reverse_priority(self):
        order = []
        mm = MiddlewareManager([
            PriorityMiddleware(0, order),
            PriorityMiddleware(10, order),
        ])
        route = make_route()
        resp = make_response()
        await mm.process_before_request(route, {})
        order.clear()
        await mm.process_after_response(resp, route, {})
        assert order.index("res:10") < order.index("res:0")

    @pytest.mark.asyncio
    async def test_response_can_modify_response(self):
        class StatusMw(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = None
            __enabled__ = True

            async def response(self, response):
                response.text = "modified"
                return response

        mm = MiddlewareManager([StatusMw()])
        route = make_route()
        resp = make_response(text="original")
        result = await mm.process_after_response(resp, route, {})
        assert result.text == "modified"

    @pytest.mark.asyncio
    async def test_response_disabled_middleware_skipped(self):
        mw = SimpleMiddleware()
        mw.__enabled__ = False
        mm = MiddlewareManager([mw])
        route = make_route()
        resp = make_response()
        await mm.process_after_response(resp, route, {})
        assert mw.responses == []

    @pytest.mark.asyncio
    async def test_response_method_filter_applied(self):
        class GetOnly(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = ["GET"]
            __enabled__ = True
            called = False

            async def response(self, response):
                GetOnly.called = True
                return response

        mm = MiddlewareManager([GetOnly()])
        resp = make_response()
        await mm.process_after_response(resp, make_route(method="POST"), {})
        assert not GetOnly.called

        await mm.process_after_response(resp, make_route(method="GET"), {})
        assert GetOnly.called

    @pytest.mark.asyncio
    async def test_empty_middleware_returns_response_unchanged(self):
        mm = MiddlewareManager()
        resp = make_response(status=201, text="created")
        result = await mm.process_after_response(resp, make_route(), {})
        assert result.status == 201
        assert result.text == "created"


# ---------------------------------------------------------------------------
# MiddlewareManager — process_on_error
# ---------------------------------------------------------------------------

class TestProcessOnError:
    @pytest.mark.asyncio
    async def test_on_error_called(self):
        mw = SimpleMiddleware()
        mm = MiddlewareManager([mw])
        route = make_route()
        error = ConnectionError("refused")
        await mm.process_on_error(error, route, {})
        assert "ConnectionError" in mw.errors

    @pytest.mark.asyncio
    async def test_on_error_skips_disabled(self):
        mw = SimpleMiddleware()
        mw.__enabled__ = False
        mm = MiddlewareManager([mw])
        await mm.process_on_error(ValueError(), make_route(), {})
        assert mw.errors == []

    @pytest.mark.asyncio
    async def test_on_error_called_for_all_active(self):
        a, b = SimpleMiddleware("a"), SimpleMiddleware("b")
        mm = MiddlewareManager([a, b])
        await mm.process_on_error(RuntimeError("oops"), make_route(), {})
        assert len(a.errors) == 1
        assert len(b.errors) == 1

    @pytest.mark.asyncio
    async def test_on_error_method_filter(self):
        class PostOnly(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = ["POST"]
            __enabled__ = True
            called = False

            async def on_error(self, error, route, config):
                PostOnly.called = True

        mm = MiddlewareManager([PostOnly()])
        await mm.process_on_error(ValueError(), make_route(method="GET"), {})
        assert not PostOnly.called


# ---------------------------------------------------------------------------
# CacheMiddleware
# ---------------------------------------------------------------------------

class TestCacheMiddleware:
    @pytest.mark.asyncio
    async def test_cache_miss_stores_response(self):
        cache = CacheMiddleware(ttl=60)
        route = make_route(params={"q": "test"})
        kwargs = {"params": route.params}

        await cache.request("GET", route.url, kwargs)
        resp = make_response(text="fresh")
        result = await cache.response(resp)

        assert result.text == "fresh"
        assert len(cache._cache) == 1

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached(self):
        cache = CacheMiddleware(ttl=60)
        kwargs = {"params": None}

        await cache.request("GET", "https://example.com", dict(kwargs))
        resp1 = make_response(text="original")
        await cache.response(resp1)

        await cache.request("GET", "https://example.com", dict(kwargs))
        resp2 = make_response(text="new")
        result = await cache.response(resp2)

        assert result.text == "original"

    @pytest.mark.asyncio
    async def test_cache_different_urls_separate_entries(self):
        cache = CacheMiddleware(ttl=60)
        kwargs = {"params": None}

        await cache.request("GET", "https://a.com", dict(kwargs))
        await cache.response(make_response(text="a"))

        await cache.request("GET", "https://b.com", dict(kwargs))
        await cache.response(make_response(text="b"))

        assert len(cache._cache) == 2

    @pytest.mark.asyncio
    async def test_cache_different_params_separate_entries(self):
        cache = CacheMiddleware(ttl=60)
        url = "https://example.com/search"

        await cache.request("GET", url, {"params": {"q": "foo"}})
        await cache.response(make_response(text="foo"))

        await cache.request("GET", url, {"params": {"q": "bar"}})
        await cache.response(make_response(text="bar"))

        assert len(cache._cache) == 2

    @pytest.mark.asyncio
    async def test_cache_post_not_cached_by_default(self):
        cache = CacheMiddleware(ttl=60)
        kwargs = {"params": None}

        await cache.request("POST", "https://example.com", dict(kwargs))
        await cache.response(make_response(text="post"))

        assert len(cache._cache) == 0

    @pytest.mark.asyncio
    async def test_cache_custom_methods(self):
        cache = CacheMiddleware(ttl=60, cache_methods=["POST"])
        kwargs = {"params": None}

        await cache.request("POST", "https://example.com", dict(kwargs))
        await cache.response(make_response(text="posted"))

        assert len(cache._cache) == 1

        await cache.request("GET", "https://example.com", dict(kwargs))
        await cache.response(make_response(text="got"))

        assert len(cache._cache) == 1

    @pytest.mark.asyncio
    async def test_cache_ttl_expiry(self):
        cache = CacheMiddleware(ttl=1)
        kwargs = {"params": None}

        await cache.request("GET", "https://example.com", dict(kwargs))
        await cache.response(make_response(text="fresh"))

        await asyncio.sleep(1.1)

        await cache.request("GET", "https://example.com", dict(kwargs))
        key, cached = cache._state.get()
        assert cached is None

        resp2 = make_response(text="refreshed")
        result = await cache.response(resp2)
        assert result.text == "refreshed"

    @pytest.mark.asyncio
    async def test_cache_max_size_evicts_oldest(self):
        cache = CacheMiddleware(ttl=60, max_size=2)
        kwargs = {"params": None}

        for url in ["https://a.com", "https://b.com", "https://c.com"]:
            await cache.request("GET", url, dict(kwargs))
            await cache.response(make_response(text=url))

        assert len(cache._cache) == 2
        urls_in_cache = [e.response.text for e in cache._cache.values()]
        assert "https://a.com" not in urls_in_cache

    @pytest.mark.asyncio
    async def test_cache_clear(self):
        cache = CacheMiddleware(ttl=60)
        kwargs = {"params": None}

        await cache.request("GET", "https://example.com", dict(kwargs))
        await cache.response(make_response())

        assert len(cache._cache) == 1
        cache.clear()
        assert len(cache._cache) == 0

    def test_cache_get_stats(self):
        cache = CacheMiddleware(ttl=120, max_size=50, cache_methods=["GET", "POST"])
        stats = cache.get_stats()
        assert stats["ttl"] == 120
        assert stats["max_size"] == 50
        assert stats["methods"] == ["GET", "POST"]
        assert stats["size"] == 0

    @pytest.mark.asyncio
    async def test_cache_on_error_invalidates(self):
        cache = CacheMiddleware(ttl=60)
        kwargs = {"params": None}

        await cache.request("GET", "https://example.com", dict(kwargs))
        await cache.response(make_response(text="cached"))
        assert len(cache._cache) == 1

        await cache.request("GET", "https://example.com", dict(kwargs))
        await cache.on_error(ConnectionError(), make_route(), {})
        assert len(cache._cache) == 0

    @pytest.mark.asyncio
    async def test_cache_context_isolation(self):
        """Two concurrent requests don't share ContextVar state."""
        cache = CacheMiddleware(ttl=60)
        results = []

        async def task(url: str, text: str) -> None:
            kwargs = {"params": None}
            await cache.request("GET", url, kwargs)
            resp = make_response(text=text)
            result = await cache.response(resp)
            results.append((url, result.text))

        await asyncio.gather(
            task("https://a.com", "response-a"),
            task("https://b.com", "response-b"),
        )

        assert len(results) == 2
        assert len(cache._cache) == 2

    @pytest.mark.asyncio
    async def test_cache_lru_move_to_end_on_hit(self):
        cache = CacheMiddleware(ttl=60, max_size=2)
        kwargs = {"params": None}

        await cache.request("GET", "https://a.com", dict(kwargs))
        await cache.response(make_response(text="a"))

        await cache.request("GET", "https://b.com", dict(kwargs))
        await cache.response(make_response(text="b"))

        # access a — moves to end, b becomes oldest
        await cache.request("GET", "https://a.com", dict(kwargs))
        await cache.response(make_response(text="a-fresh"))

        # add c — should evict b (oldest)
        await cache.request("GET", "https://c.com", dict(kwargs))
        await cache.response(make_response(text="c"))

        texts = [e.response.text for e in cache._cache.values()]
        assert "b" not in texts
        assert "a" in texts


# ---------------------------------------------------------------------------
# CacheEntry
# ---------------------------------------------------------------------------

class TestCacheEntry:
    def test_expires_at_set_correctly(self):
        resp = make_response()
        before = time.time()
        entry = CacheEntry(resp, ttl=60)
        after = time.time()
        assert before + 60 <= entry.expires_at <= after + 60

    def test_not_expired(self):
        entry = CacheEntry(make_response(), ttl=60)
        assert time.time() < entry.expires_at

    def test_expired(self):
        entry = CacheEntry(make_response(), ttl=0)
        assert time.time() >= entry.expires_at


# ---------------------------------------------------------------------------
# HTTPMethod literal
# ---------------------------------------------------------------------------

class TestHTTPMethod:
    def test_http_method_values(self):
        from fasthttp.types import HTTPMethod
        from typing import get_args
        args = get_args(HTTPMethod)
        assert "GET" in args
        assert "POST" in args
        assert "PUT" in args
        assert "PATCH" in args
        assert "DELETE" in args

    def test_http_method_count(self):
        from fasthttp.types import HTTPMethod
        from typing import get_args
        assert len(get_args(HTTPMethod)) == 7


# ---------------------------------------------------------------------------
# Integration — FastHTTP + middleware
# ---------------------------------------------------------------------------

class TestMiddlewareIntegration:
    def test_fasthttp_accepts_list(self):
        from fasthttp import FastHTTP
        app = FastHTTP(middleware=[SimpleMiddleware("a"), SimpleMiddleware("b")])
        assert len(app.middleware_manager.middlewares) == 2

    def test_fasthttp_accepts_chain(self):
        from fasthttp import FastHTTP
        chain = SimpleMiddleware("a") | SimpleMiddleware("b")
        app = FastHTTP(middleware=chain)
        assert len(app.middleware_manager.middlewares) == 2

    def test_fasthttp_accepts_single(self):
        from fasthttp import FastHTTP
        app = FastHTTP(middleware=SimpleMiddleware())
        assert len(app.middleware_manager.middlewares) == 1

    def test_fasthttp_no_middleware(self):
        from fasthttp import FastHTTP
        app = FastHTTP()
        assert app.middleware_manager.middlewares == []

    @pytest.mark.asyncio
    async def test_full_request_response_cycle(self):
        order = []

        class TrackMw(BaseMiddleware):
            __return_type__ = None
            __priority__ = 0
            __methods__ = None
            __enabled__ = True

            def __init__(self, name):
                self.name = name

            async def request(self, method, url, kwargs):
                order.append(f"req:{self.name}")
                return kwargs

            async def response(self, response):
                order.append(f"res:{self.name}")
                return response

        a, b, c = TrackMw("a"), TrackMw("b"), TrackMw("c")
        mm = MiddlewareManager([a, b, c])
        route = make_route()
        resp = make_response()

        await mm.process_before_request(route, {})
        await mm.process_after_response(resp, route, {})

        assert order == ["req:a", "req:b", "req:c", "res:c", "res:b", "res:a"]

    @pytest.mark.asyncio
    async def test_cache_middleware_in_manager(self):
        cache = CacheMiddleware(ttl=60)
        mm = MiddlewareManager([cache])
        route = make_route(url="https://api.example.com/data")

        config1 = await mm.process_before_request(route, {})
        resp1 = make_response(text="data")
        result1 = await mm.process_after_response(resp1, route, config1)
        assert result1.text == "data"
        assert cache.get_stats()["size"] == 1

        config2 = await mm.process_before_request(route, {})
        resp2 = make_response(text="new-data")
        result2 = await mm.process_after_response(resp2, route, config2)
        assert result2.text == "data"
