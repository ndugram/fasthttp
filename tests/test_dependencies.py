import pytest
from unittest.mock import MagicMock

from fasthttp.dependencies import Dependency, Depends


class TestDependency:
    def test_dependency_creation(self):
        async def mock_func(route, config):
            return config

        dep = Dependency(mock_func, use_cache=True)
        assert dep.func == mock_func
        assert dep.use_cache is True
        assert dep.__name__ == "mock_func"

    def test_dependency_with_use_cache_false(self):
        async def mock_func(route, config):
            return config

        dep = Dependency(mock_func, use_cache=False)
        assert dep.use_cache is False

    def test_dependency_with_scope(self):
        async def mock_func(route, config):
            return config

        dep = Dependency(mock_func, use_cache=True, scope="function")
        assert dep.scope == "function"

    def test_depends_function(self):
        async def mock_func(route, config):
            return config

        dep = Depends(mock_func)
        assert isinstance(dep, Dependency)
        assert dep.func == mock_func

    def test_depends_with_use_cache(self):
        async def mock_func(route, config):
            return config

        dep = Depends(mock_func, use_cache=False)
        assert dep.use_cache is False

    def test_depends_with_scope(self):
        async def mock_func(route, config):
            return config

        dep = Depends(mock_func, scope="request")
        assert dep.scope == "request"

    @pytest.mark.asyncio
    async def test_dependency_call_modifies_config(self):
        async def mock_func(route, config):
            config.setdefault("headers", {})["X-Test"] = "value"
            return config

        dep = Dependency(mock_func)
        route = MagicMock()
        config = {}

        result = await dep(route, config)
        assert result["headers"]["X-Test"] == "value"

    @pytest.mark.asyncio
    async def test_dependency_call_returns_modified_config(self):
        async def mock_func(route, config):
            config["custom_key"] = "custom_value"
            return config

        dep = Dependency(mock_func)
        route = MagicMock()
        config = {}

        result = await dep(route, config)
        assert result["custom_key"] == "custom_value"

    @pytest.mark.asyncio
    async def test_dependency_receives_route_and_config(self):
        received_route = None
        received_config = None

        async def mock_func(route, config):
            nonlocal received_route, received_config
            received_route = route
            received_config = config
            return config

        dep = Dependency(mock_func)
        route = MagicMock()
        config = {"test": True}

        await dep(route, config)
        assert received_route == route
        assert received_config == config

    @pytest.mark.asyncio
    async def test_sync_dependency(self):
        def sync_func(route, config):
            config.setdefault("headers", {})["X-Sync"] = "value"
            return config

        dep = Dependency(sync_func)
        route = MagicMock()
        config = {}

        result = await dep(route, config)
        assert result["headers"]["X-Sync"] == "value"
