import logging
from typing import Any
from unittest.mock import AsyncMock

import pytest

from fasthttp.client import HTTPClient
from fasthttp.middleware import MiddlewareManager as MM  # noqa: N817
from fasthttp.response import Response

logger = logging.getLogger("test")


@pytest.fixture
def mock_logger() -> logging.Logger:
    """Create a mock logger for testing."""
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def sample_response() -> Response:
    """Create a sample Response object for testing."""
    return Response(
        status=200,
        text='{"message": "success"}',
        headers={"Content-Type": "application/json"},
        method="GET",
        req_headers={"User-Agent": "fasthttp/0.1.6"},
        query={"key": "value"},
        req_json={"data": "test"},
        req_data=None,
    )


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Create a mock httpx AsyncClient for testing."""
    return AsyncMock()


@pytest.fixture
def request_configs() -> dict[str, Any]:
    """Create default request configurations for testing."""
    return {
        "GET": {"headers": {"Accept": "application/json"}, "timeout": 30.0},
        "POST": {"headers": {"Content-Type": "application/json"}, "timeout": 30.0},
        "PUT": {"headers": {"Content-Type": "application/json"}, "timeout": 30.0},
        "DELETE": {"timeout": 30.0},
    }


@pytest.fixture
def http_client(mock_logger, request_configs) -> HTTPClient:
    """Create an HTTPClient instance for testing."""
    return HTTPClient(
        request_configs=request_configs,
        logger=mock_logger,
    )


@pytest.fixture
def middleware_manager() -> MM:
    """Create a MiddlewareManager instance for testing."""
    return MM()
