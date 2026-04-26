"""Tests for Route, Router, and URL helpers."""
import pytest
from pydantic import BaseModel

from fasthttp.routing import Route, Router
from fasthttp.helpers.routing import (
    apply_base_url,
    check_https_url,
    join_prefix,
    resolve_url,
)
from fasthttp.response import Response


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def dummy_handler(resp: Response) -> Response:
    return resp


# ---------------------------------------------------------------------------
# check_https_url
# ---------------------------------------------------------------------------

class TestCheckHttpsUrl:
    def test_already_https(self):
        assert check_https_url(url="https://example.com") == "https://example.com"

    def test_already_http(self):
        assert check_https_url(url="http://example.com") == "http://example.com"

    def test_no_scheme_adds_https(self):
        assert check_https_url(url="example.com") == "https://example.com"

    def test_strips_whitespace(self):
        assert check_https_url(url="  example.com  ") == "https://example.com"

    def test_path_only_no_scheme(self):
        result = check_https_url(url="api.example.com/v1")
        assert result.startswith("https://")

    def test_empty_string_adds_https(self):
        result = check_https_url(url="")
        assert result == "https://"


# ---------------------------------------------------------------------------
# join_prefix
# ---------------------------------------------------------------------------

class TestJoinPrefix:
    def test_empty_prefix_returns_url(self):
        assert join_prefix("", "/users") == "/users"

    def test_empty_prefix_and_empty_url(self):
        assert join_prefix("", "") == ""

    def test_prefix_and_path(self):
        assert join_prefix("/v1", "/users") == "/v1/users"

    def test_prefix_without_leading_slash(self):
        assert join_prefix("v1", "/users") == "/v1/users"

    def test_prefix_with_trailing_slash_stripped(self):
        assert join_prefix("/v1/", "/users") == "/v1/users"

    def test_url_without_leading_slash(self):
        assert join_prefix("/v1", "users") == "/v1/users"

    def test_url_is_root(self):
        assert join_prefix("/v1", "/") == "/v1"

    def test_nested_prefix(self):
        assert join_prefix("/api/v2", "/items") == "/api/v2/items"


# ---------------------------------------------------------------------------
# resolve_url
# ---------------------------------------------------------------------------

class TestResolveUrl:
    def test_absolute_url_returned_unchanged(self):
        url = "https://example.com/api"
        assert resolve_url(url=url, base_url=None, prefix="") == url

    def test_http_absolute_unchanged(self):
        url = "http://example.com/api"
        assert resolve_url(url=url, base_url=None, prefix="") == url

    def test_no_scheme_no_base_adds_https(self):
        result = resolve_url(url="example.com/api", base_url=None, prefix="")
        assert result == "https://example.com/api"

    def test_path_without_base_raises(self):
        with pytest.raises(ValueError, match="base_url"):
            resolve_url(url="/users", base_url=None, prefix="")

    def test_relative_with_base_url(self):
        result = resolve_url(url="/users", base_url="https://api.example.com", prefix="")
        assert result == "https://api.example.com/users"

    def test_relative_with_base_and_prefix(self):
        result = resolve_url(url="/items", base_url="https://api.example.com", prefix="/v1")
        assert result == "https://api.example.com/v1/items"

    def test_base_url_without_scheme(self):
        result = resolve_url(url="/users", base_url="api.example.com", prefix="")
        assert result.startswith("https://")
        assert "users" in result


# ---------------------------------------------------------------------------
# apply_base_url
# ---------------------------------------------------------------------------

class TestApplyBaseUrl:
    def test_absolute_unchanged(self):
        url = "https://example.com/path"
        assert apply_base_url(url=url, base_url=None) == url

    def test_no_base_adds_https(self):
        result = apply_base_url(url="example.com/path", base_url=None)
        assert result == "https://example.com/path"

    def test_with_base_url(self):
        result = apply_base_url(url="users", base_url="https://api.example.com")
        assert result == "https://api.example.com/users"

    def test_with_base_url_trailing_slash(self):
        result = apply_base_url(url="users", base_url="https://api.example.com/")
        assert result == "https://api.example.com/users"

    def test_with_base_url_leading_slash(self):
        result = apply_base_url(url="/users", base_url="https://api.example.com")
        assert result == "https://api.example.com/users"


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

class TestRoute:
    def test_route_creation_minimal(self):
        route = Route(method="GET", url="https://example.com", handler=dummy_handler)
        assert route.method == "GET"
        assert route.url == "https://example.com"
        assert route.handler is dummy_handler

    def test_route_defaults(self):
        route = Route(method="GET", url="https://example.com", handler=dummy_handler)
        assert route.params is None
        assert route.json is None
        assert route.data is None
        assert route.tags == []
        assert route.dependencies == []
        assert route.skip_request is False
        assert route.responses == {}
        assert route.response_model is None
        assert route.request_model is None

    def test_route_with_params(self):
        route = Route(
            method="GET",
            url="https://example.com/search",
            handler=dummy_handler,
            params={"q": "test", "page": "1"},
        )
        assert route.params == {"q": "test", "page": "1"}

    def test_route_with_json(self):
        route = Route(
            method="POST",
            url="https://example.com/api",
            handler=dummy_handler,
            json={"name": "test", "value": 42},
        )
        assert route.json == {"name": "test", "value": 42}

    def test_route_with_data(self):
        route = Route(
            method="POST",
            url="https://example.com/upload",
            handler=dummy_handler,
            data=b"binary content",
        )
        assert route.data == b"binary content"

    def test_route_with_tags(self):
        route = Route(
            method="GET",
            url="https://example.com/api",
            handler=dummy_handler,
            tags=["users", "admin"],
        )
        assert route.tags == ["users", "admin"]

    def test_route_tags_none_becomes_empty(self):
        route = Route(method="GET", url="https://example.com", handler=dummy_handler, tags=None)
        assert route.tags == []

    def test_route_dependencies_none_becomes_empty(self):
        route = Route(method="GET", url="https://example.com", handler=dummy_handler, dependencies=None)
        assert route.dependencies == []

    def test_route_skip_request(self):
        route = Route(
            method="GET",
            url="https://example.com",
            handler=dummy_handler,
            skip_request=True,
        )
        assert route.skip_request is True

    def test_route_all_http_methods(self):
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            route = Route(method=method, url="https://example.com", handler=dummy_handler)
            assert route.method == method

    def test_route_with_response_model(self):
        class UserModel(BaseModel):
            name: str
            age: int

        route = Route(
            method="GET",
            url="https://example.com/user",
            handler=dummy_handler,
            response_model=UserModel,
        )
        assert route.response_model is UserModel

    def test_route_with_request_model(self):
        class CreateUser(BaseModel):
            name: str

        route = Route(
            method="POST",
            url="https://example.com/user",
            handler=dummy_handler,
            request_model=CreateUser,
        )
        assert route.request_model is CreateUser

    def test_route_with_responses(self):
        class Error404(BaseModel):
            detail: str

        route = Route(
            method="GET",
            url="https://example.com/api",
            handler=dummy_handler,
            responses={404: {"model": Error404}},
        )
        assert 404 in route.responses

    def test_route_responses_none_becomes_empty(self):
        route = Route(method="GET", url="https://example.com", handler=dummy_handler, responses=None)
        assert route.responses == {}


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class TestRouter:
    def test_router_creation_defaults(self):
        router = Router()
        assert router.base_url is None
        assert router.prefix == ""
        assert router.tags == []
        assert router.dependencies == []

    def test_router_creation_with_params(self):
        router = Router(
            base_url="https://api.example.com",
            prefix="/v1",
            tags=["users"],
        )
        assert router.base_url == "https://api.example.com"
        assert router.prefix == "/v1"
        assert router.tags == ["users"]

    def test_router_get_decorator(self):
        router = Router(base_url="https://api.example.com")

        @router.get(url="/users")
        async def get_users(resp: Response) -> list:
            return []

        assert len(router._route_defs) == 1
        assert router._route_defs[0].method == "GET"

    def test_router_post_decorator(self):
        router = Router(base_url="https://api.example.com")

        @router.post(url="/users")
        async def create_user(resp: Response) -> dict:
            return {}

        assert router._route_defs[0].method == "POST"

    def test_router_put_decorator(self):
        router = Router(base_url="https://api.example.com")

        @router.put(url="/users/1")
        async def update_user(resp: Response) -> dict:
            return {}

        assert router._route_defs[0].method == "PUT"

    def test_router_patch_decorator(self):
        router = Router(base_url="https://api.example.com")

        @router.patch(url="/users/1")
        async def partial_update(resp: Response) -> dict:
            return {}

        assert router._route_defs[0].method == "PATCH"

    def test_router_delete_decorator(self):
        router = Router(base_url="https://api.example.com")

        @router.delete(url="/users/1")
        async def delete_user(resp: Response) -> None:
            pass

        assert router._route_defs[0].method == "DELETE"

    def test_router_multiple_routes(self):
        router = Router(base_url="https://api.example.com")

        @router.get(url="/users")
        async def get_users(resp: Response) -> list:
            return []

        @router.post(url="/users")
        async def create_user(resp: Response) -> dict:
            return {}

        @router.delete(url="/users/1")
        async def delete_user(resp: Response) -> None:
            pass

        assert len(router._route_defs) == 3

    def test_router_include_router(self):
        parent = Router(base_url="https://api.example.com", prefix="/v1")
        child = Router()

        parent.include_router(child, prefix="/admin")
        assert len(parent._include_defs) == 1
        assert parent._include_defs[0].prefix == "/admin"

    def test_router_include_router_with_tags(self):
        parent = Router(base_url="https://api.example.com")
        child = Router()

        parent.include_router(child, tags=["admin"])
        assert parent._include_defs[0].tags == ["admin"]

    def test_router_include_router_with_base_url(self):
        parent = Router()
        child = Router()

        parent.include_router(child, base_url="https://other.example.com")
        assert parent._include_defs[0].base_url == "https://other.example.com"

    def test_router_tags_none_becomes_empty(self):
        router = Router(tags=None)
        assert router.tags == []

    def test_router_dependencies_none_becomes_empty(self):
        router = Router(dependencies=None)
        assert router.dependencies == []

    def test_router_route_inherits_tags(self):
        router = Router(base_url="https://api.example.com", tags=["shared"])

        @router.get(url="/users")
        async def get_users(resp: Response) -> list:
            return []

        assert router._route_defs[0].tags == []

    def test_router_route_with_params(self):
        router = Router(base_url="https://api.example.com")

        @router.get(url="/search", params={"limit": "10"})
        async def search(resp: Response) -> list:
            return []

        assert router._route_defs[0].params == {"limit": "10"}

    def test_router_route_with_json(self):
        router = Router(base_url="https://api.example.com")

        @router.post(url="/users", json={"role": "admin"})
        async def create(resp: Response) -> dict:
            return {}

        assert router._route_defs[0].json == {"role": "admin"}


# ---------------------------------------------------------------------------
# FastHTTP include_router integration
# ---------------------------------------------------------------------------

class TestFastHTTPIncludeRouter:
    def test_include_router_adds_routes(self):
        from fasthttp import FastHTTP

        router = Router(base_url="https://api.example.com")

        @router.get(url="/users")
        async def get_users(resp: Response) -> list:
            return []

        app = FastHTTP()
        app.include_router(router)
        assert any(r.url for r in app.routes)

    def test_include_router_with_prefix(self):
        from fasthttp import FastHTTP

        router = Router(base_url="https://api.example.com")

        @router.get(url="/items")
        async def get_items(resp: Response) -> list:
            return []

        app = FastHTTP()
        app.include_router(router, prefix="/v2")
        assert len(app.routes) >= 1

    def test_nested_routers_included(self):
        from fasthttp import FastHTTP

        child = Router(base_url="https://api.example.com")

        @child.get(url="/child-route")
        async def child_handler(resp: Response) -> dict:
            return {}

        parent = Router(base_url="https://api.example.com")
        parent.include_router(child)

        app = FastHTTP()
        app.include_router(parent)
        assert len(app.routes) >= 1
