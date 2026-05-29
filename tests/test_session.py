from unittest.mock import AsyncMock, patch

import pytest

from fasthttp.response import Response
from fasthttp.session import AsyncSession


def _mock_resp(status: int = 200, text: str = "ok") -> Response:
    return Response(status=status, text=text, headers={})


class TestAsyncSession:
    def test_creation_defaults(self) -> None:
        session = AsyncSession()
        assert session.base_url is None
        assert session.http2_enabled is False
        assert session.proxy is None
        assert session._client is None  # noqa: SLF001

    def test_creation_with_options(self) -> None:
        session = AsyncSession(
            base_url="https://api.example.com",
            headers={"X-Token": "abc"},
            timeout=5.0,
            http2=True,
            security=False,
        )
        assert session.base_url == "https://api.example.com"
        assert session.http2_enabled is True
        assert session._session_headers == {"X-Token": "abc"}  # noqa: SLF001

    def test_ensure_open_raises_when_closed(self) -> None:
        session = AsyncSession()
        with pytest.raises(RuntimeError, match="not open"):
            session._ensure_open()  # noqa: SLF001

    @pytest.mark.asyncio
    async def test_context_manager_opens_and_closes(self) -> None:
        async with AsyncSession(security=False) as session:
            assert session._client is not None  # noqa: SLF001
        assert session._client is None  # noqa: SLF001

    @pytest.mark.asyncio
    async def test_open_close_manual(self) -> None:
        session = AsyncSession(security=False)
        await session.open()
        assert session._client is not None  # noqa: SLF001
        await session.close()
        assert session._client is None  # noqa: SLF001

    @pytest.mark.asyncio
    async def test_get_request(self) -> None:
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client,
                "send",
                AsyncMock(return_value=_mock_resp(200, '{"id": 1}')),
            ):  # noqa: SLF001
                resp = await session.get("https://example.com/api/1")

        assert resp is not None
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_post_request_with_json(self) -> None:
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client,
                "send",
                AsyncMock(return_value=_mock_resp(201, '{"created": true}')),
            ):  # noqa: SLF001
                resp = await session.post(
                    "https://example.com/api", json={"name": "test"}
                )

        assert resp is not None
        assert resp.status == 201

    @pytest.mark.asyncio
    async def test_put_request(self) -> None:
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client, "send", AsyncMock(return_value=_mock_resp(200))
            ):  # noqa: SLF001
                resp = await session.put(
                    "https://example.com/api/1", json={"name": "updated"}
                )

        assert resp is not None
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_patch_request(self) -> None:
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client, "send", AsyncMock(return_value=_mock_resp(200))
            ):  # noqa: SLF001
                resp = await session.patch(
                    "https://example.com/api/1", json={"field": "value"}
                )

        assert resp is not None
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_delete_request(self) -> None:
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client,
                "send",
                AsyncMock(return_value=_mock_resp(204, "")),
            ):  # noqa: SLF001
                resp = await session.delete("https://example.com/api/1")

        assert resp is not None
        assert resp.status == 204

    @pytest.mark.asyncio
    async def test_get_with_params(self) -> None:
        mock_send = AsyncMock(return_value=_mock_resp(200, "[]"))
        async with AsyncSession(security=False) as session:
            with patch.object(session._http_client, "send", mock_send):  # noqa: SLF001
                await session.get(
                    "https://example.com/api", params={"page": 1, "limit": 10}
                )

        route = mock_send.call_args.args[1]
        assert route.params == {"page": 1, "limit": 10}

    @pytest.mark.asyncio
    async def test_per_request_headers_applied(self) -> None:
        mock_send = AsyncMock(return_value=_mock_resp(200))
        async with AsyncSession(security=False) as session:
            with patch.object(session._http_client, "send", mock_send):  # noqa: SLF001
                await session.get(
                    "https://example.com/api",
                    headers={"X-Request": "request-value"},
                )

        route = mock_send.call_args.args[1]
        # per-request header injected as a dependency
        assert len(route.dependencies) == 1

    @pytest.mark.asyncio
    async def test_base_url_resolved(self) -> None:
        mock_send = AsyncMock(return_value=_mock_resp(200))
        async with AsyncSession(
            base_url="https://api.example.com", security=False
        ) as session:
            with patch.object(session._http_client, "send", mock_send):  # noqa: SLF001
                await session.get("/users")

        route = mock_send.call_args.args[1]
        assert "api.example.com" in route.url
        assert "/users" in route.url

    @pytest.mark.asyncio
    async def test_generic_request_method(self) -> None:
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client, "send", AsyncMock(return_value=_mock_resp(200))
            ):  # noqa: SLF001
                resp = await session.request("GET", "https://example.com/api")

        assert resp is not None
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_4xx_returns_none(self) -> None:
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client, "send", AsyncMock(return_value=None)
            ):  # noqa: SLF001
                resp = await session.get("https://example.com/missing")

        assert resp is None

    @pytest.mark.asyncio
    async def test_connection_error_returns_none(self) -> None:
        # HTTPClient.send catches ConnectError internally and returns None
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client, "send", AsyncMock(return_value=None)
            ):  # noqa: SLF001
                resp = await session.get("https://example.com/api")

        assert resp is None

    @pytest.mark.asyncio
    async def test_timeout_error_returns_none(self) -> None:
        # HTTPClient.send catches TimeoutException internally and returns None
        async with AsyncSession(security=False) as session:
            with patch.object(
                session._http_client, "send", AsyncMock(return_value=None)
            ):  # noqa: SLF001
                resp = await session.get("https://example.com/api")

        assert resp is None

    @pytest.mark.asyncio
    async def test_correct_method_passed_to_route(self) -> None:
        for method in ("get", "post", "put", "patch", "delete"):
            mock_send = AsyncMock(return_value=_mock_resp(200))
            async with AsyncSession(security=False) as session:
                with patch.object(session._http_client, "send", mock_send):  # noqa: SLF001
                    await getattr(session, method)("https://example.com/api")

            route = mock_send.call_args.args[1]
            assert route.method == method.upper()

    @pytest.mark.asyncio
    async def test_session_request_configs_set_per_method(self) -> None:
        session = AsyncSession(
            headers={"X-Token": "tok"},
            timeout=15.0,
            security=False,
        )
        for method in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            cfg = session._request_configs[method]  # noqa: SLF001
            assert cfg["timeout"] == 15.0
            assert cfg["headers"]["X-Token"] == "tok"
