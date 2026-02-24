import json
import pytest

from fasthttp.response import Response


class TestResponse:
    """Tests for the Response class."""

    def test_response_creation(self) -> None:
        """Test that Response can be created with required parameters."""
        response = Response(
            status=200,
            text="Hello World",
            headers={"Content-Type": "text/plain"},
        )

        assert response.status == 200
        assert response.text == "Hello World"
        assert response.headers == {"Content-Type": "text/plain"}

    def test_response_with_all_parameters(self) -> None:
        """Test Response creation with all optional parameters."""
        response = Response(
            status=201,
            text='{"created": true}',
            headers={"Content-Type": "application/json"},
            method="POST",
            req_headers={"Authorization": "Bearer token"},
            query={"page": "1"},
            req_json={"name": "test"},
            req_data=None,
        )

        assert response.status == 201
        assert response.method == "POST"
        assert response.req_headers == {"Authorization": "Bearer token"}
        assert response.query == {"page": "1"}
        assert response.req_json() == {"name": "test"}

    def test_response_json_parsing(self) -> None:
        """Test that json() method correctly parses JSON response."""
        response = Response(
            status=200,
            text='{"key": "value", "number": 42}',
            headers={"Content-Type": "application/json"},
        )

        result = response.json()

        assert result == {"key": "value", "number": 42}

    def test_response_json_parsing_invalid_json(self) -> None:
        """Test that json() raises ValueError for invalid JSON."""
        response = Response(
            status=200,
            text="not valid json",
            headers={"Content-Type": "text/plain"},
        )

        with pytest.raises(json.JSONDecodeError):
            response.json()

    def test_response_method_property(self) -> None:
        """Test the method property getter and setter."""
        response = Response(
            status=200,
            text="",
            headers={},
            method=None,
        )

        assert response.method is None

        response.method = "POST"
        assert response.method == "POST"

    def test_response_req_headers_property(self) -> None:
        """Test the req_headers property getter and setter."""
        response = Response(
            status=200,
            text="",
            headers={},
        )

        assert response.req_headers is None

        response.req_headers = {"X-Custom": "header"}
        assert response.req_headers == {"X-Custom": "header"}

    def test_response_query_property(self) -> None:
        """Test the query property getter and setter."""
        response = Response(
            status=200,
            text="",
            headers={},
        )

        assert response.query is None

        response.query = {"search": "query"}
        assert response.query == {"search": "query"}

    def test_response_path_params_property(self) -> None:
        """Test that path_params returns empty dict."""
        response = Response(
            status=200,
            text="",
            headers={},
        )

        assert response.path_params == {}

    def test_response_req_json_method(self) -> None:
        """Test the req_json() method returns request JSON."""
        response = Response(
            status=200,
            text="",
            headers={},
            req_json={"submit": True},
        )

        assert response.req_json() == {"submit": True}

    def test_response_req_text_with_json(self) -> None:
        """Test req_text() returns JSON string for JSON requests."""
        response = Response(
            status=200,
            text="",
            headers={},
            req_json={"key": "value"},
        )

        result = response.req_text()
        assert result == '{"key": "value"}'

    def test_response_req_text_with_data(self) -> None:
        """Test req_text() returns string for raw data requests."""
        response = Response(
            status=200,
            text="",
            headers={},
            req_data={"form": "data"},
        )

        result = response.req_text()
        assert result == "{'form': 'data'}"

    def test_response_req_text_returns_none(self) -> None:
        """Test req_text() returns None when no body data."""
        response = Response(
            status=200,
            text="",
            headers={},
        )

        assert response.req_text() is None

    def test_response_repr(self) -> None:
        """Test the __repr__ method returns correct format."""
        response = Response(
            status=404,
            text="Not Found",
            headers={},
        )

        assert repr(response) == "<Response [404]>"

    def test_response_handler_result_stored(self, sample_response) -> None:
        """Test that handler result is stored in response."""
        sample_response._handler_result = "processed result"
        assert sample_response._handler_result == "processed result"
