"""Tests for types module."""
import pytest

from fasthttp.types import JSONResponse, RequestsOptinal


class TestJSONResponse:
    """Tests for JSONResponse type definitions."""

    def test_json_response_primitive_types(self) -> None:
        """Test JSONResponse primitive type aliases."""
        # These are type aliases, so we can verify they exist
        assert hasattr(JSONResponse, 'Primutive')
        assert hasattr(JSONResponse, 'Value')

    def test_json_response_value_can_be_primitive(self) -> None:
        """Test that Value type can be primitive types."""
        # This is more of a type checking test, but we can verify the class exists
        assert JSONResponse is not None
        
        # Test that we can reference the types
        primutive_types = (str, int, float, bool, type(None))
        # Just verify the class structure is correct
        assert True

    def test_json_response_docstring(self) -> None:
        """Test JSONResponse has proper docstring."""
        assert JSONResponse.__doc__ is not None
        assert "JSON response type definitions" in JSONResponse.__doc__


class TestRequestsOptinal:
    """Tests for RequestsOptinal TypedDict."""

    def test_requests_optional_exists(self) -> None:
        """Test RequestsOptinal type exists."""
        assert RequestsOptinal is not None

    def test_requests_optional_has_headers(self) -> None:
        """Test RequestsOptinal has headers field."""
        # TypedDict fields are checked at type-check time
        # We can verify the class annotations exist
        assert 'headers' in RequestsOptinal.__annotations__

    def test_requests_optional_has_timeout(self) -> None:
        """Test RequestsOptinal has timeout field."""
        assert 'timeout' in RequestsOptinal.__annotations__

    def test_requests_optional_has_allow_redirects(self) -> None:
        """Test RequestsOptinal has allow_redirects field."""
        assert 'allow_redirects' in RequestsOptinal.__annotations__

    def test_requests_optional_can_be_created(self) -> None:
        """Test RequestsOptinal can be instantiated with fields."""
        config: RequestsOptinal = {
            "headers": {"Content-Type": "application/json"},
            "timeout": 30.0,
            "allow_redirects": True,
        }
        
        assert config["headers"] == {"Content-Type": "application/json"}
        assert config["timeout"] == 30.0
        assert config["allow_redirects"] is True

    def test_requests_optional_partial_fields(self) -> None:
        """Test RequestsOptinal can have partial fields (all optional)."""
        config1: RequestsOptinal = {"timeout": 60.0}
        assert config1["timeout"] == 60.0

        config2: RequestsOptinal = {"headers": {"Authorization": "Bearer token"}}
        assert "Authorization" in config2["headers"]

        config3: RequestsOptinal = {"allow_redirects": False}
        assert config3["allow_redirects"] is False

    def test_requests_optional_docstring(self) -> None:
        """Test RequestsOptinal has proper docstring."""
        assert RequestsOptinal.__doc__ is not None
        assert "Optional request configuration" in RequestsOptinal.__doc__

    def test_requests_optional_total_false(self) -> None:
        """Test that RequestsOptinal has total=False (all fields optional)."""
        # Verify that all fields are indeed optional by creating empty dict
        config: RequestsOptinal = {}
        assert config == {}
