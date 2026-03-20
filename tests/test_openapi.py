"""Tests for OpenAPI schema generation."""
import pytest
from pydantic import BaseModel

from fasthttp import FastHTTP
from fasthttp.response import Response
from fasthttp.openapi.generator import (
    generate_openapi_schema,
    _get_type_string,
    _extract_docstring,
    _generate_schema_from_model,
    _generate_parameter_schema,
    _generate_response_schema,
    _normalize_path,
)


class TestGetTypeString:
    """Tests for _get_type_string function."""

    def test_get_type_string_str(self) -> None:
        """Test type string for str type."""
        result = _get_type_string(str)
        assert result == {"type": "string"}

    def test_get_type_string_int(self) -> None:
        """Test type string for int type."""
        result = _get_type_string(int)
        assert result == {"type": "integer"}

    def test_get_type_string_float(self) -> None:
        """Test type string for float type."""
        result = _get_type_string(float)
        assert result == {"type": "number"}

    def test_get_type_string_bool(self) -> None:
        """Test type string for bool type."""
        result = _get_type_string(bool)
        assert result == {"type": "boolean"}

    def test_get_type_string_list(self) -> None:
        """Test type string for list type."""
        result = _get_type_string(list)
        assert result == {"type": "array"}

    def test_get_type_string_dict(self) -> None:
        """Test type string for dict type."""
        result = _get_type_string(dict)
        assert result == {"type": "object"}

    def test_get_type_string_none(self) -> None:
        """Test type string for None type."""
        result = _get_type_string(None)
        assert result == {"type": "string", "nullable": True}


class TestExtractDocstring:
    """Tests for _extract_docstring function."""

    def test_extract_docstring_basic(self) -> None:
        """Test extracting docstring from function."""
        def example_func():
            """This is a test function."""
            pass

        result = _extract_docstring(example_func)
        assert "test function" in result

    def test_extract_docstring_none(self) -> None:
        """Test extracting docstring from function without docstring."""
        def no_doc_func():
            pass

        result = _extract_docstring(no_doc_func)
        assert result == ""

    def test_extract_docstring_multiline(self) -> None:
        """Test extracting multiline docstring."""
        def multiline_func():
            """
            This is a multiline
            docstring for testing.
            """
            pass

        result = _extract_docstring(multiline_func)
        assert "multiline" in result
        assert "docstring" in result


class TestGenerateSchemaFromModel:
    """Tests for _generate_schema_from_model function."""

    def test_generate_schema_basic_model(self) -> None:
        """Test generating schema from basic Pydantic model."""
        class UserModel(BaseModel):
            name: str
            age: int

        result = _generate_schema_from_model(UserModel)

        assert result["type"] == "object"
        assert "name" in result["properties"]
        assert "age" in result["properties"]
        assert "name" in result["required"]
        assert "age" in result["required"]

    def test_generate_schema_with_optional_fields(self) -> None:
        """Test generating schema with optional fields."""
        from typing import Optional

        class OptionalModel(BaseModel):
            required_field: str
            optional_field: Optional[str] = None

        result = _generate_schema_from_model(OptionalModel)

        assert "required_field" in result["required"]
        # optional_field should not be in required list
        assert "optional_field" not in result.get("required", [])


class TestGenerateParameterSchema:
    """Tests for _generate_parameter_schema function."""

    def test_generate_parameter_schema_basic(self) -> None:
        """Test generating parameter schema from params dict."""
        params = {"page": "1", "limit": "10"}

        result = _generate_parameter_schema(params)

        assert result["type"] == "object"
        assert "page" in result["properties"]
        assert "limit" in result["properties"]
        assert result["required"] == ["page", "limit"]

    def test_generate_parameter_schema_none(self) -> None:
        """Test generating parameter schema from None."""
        result = _generate_parameter_schema(None)
        assert result == {}


class TestGenerateResponseSchema:
    """Tests for _generate_response_schema function."""

    def test_generate_response_schema_none(self) -> None:
        """Test generating response schema without model."""
        result = _generate_response_schema(None)

        assert result["description"] == "Successful response"

    def test_generate_response_schema_with_model(self) -> None:
        """Test generating response schema with Pydantic model."""
        class ResponseModel(BaseModel):
            id: int
            name: str

        result = _generate_response_schema(ResponseModel)

        assert "content" in result
        assert "application/json" in result["content"]
        assert "$ref" in result["content"]["application/json"]["schema"]


class TestNormalizePath:
    """Tests for _normalize_path function."""

    def test_normalize_path_https(self) -> None:
        """Test normalizing HTTPS URL."""
        result = _normalize_path("https://example.com/api/users")
        assert result == "/example.com/api/users"

    def test_normalize_path_http(self) -> None:
        """Test normalizing HTTP URL."""
        result = _normalize_path("http://example.com/api")
        assert result == "/example.com/api"

    def test_normalize_path_with_port(self) -> None:
        """Test normalizing URL with port."""
        result = _normalize_path("https://example.com:8080/api")
        assert "example.com_8080" in result

    def test_normalize_path_root(self) -> None:
        """Test normalizing root URL."""
        result = _normalize_path("https://example.com")
        assert result == "/example.com/"

    def test_normalize_path_with_query(self) -> None:
        """Test normalizing URL with query string."""
        result = _normalize_path("https://example.com/api?page=1")
        assert "page=1" in result


class TestGenerateOpenAPISchema:
    """Tests for generate_openapi_schema function."""

    def test_generate_openapi_schema_basic(self) -> None:
        """Test generating OpenAPI schema from basic FastHTTP app."""
        app = FastHTTP()

        @app.get(url="https://example.com/api/users")
        async def get_users(resp: Response) -> dict:
            """Get all users."""
            return resp.json()

        schema = generate_openapi_schema(app)

        assert schema["openapi"] == "3.0.3"
        assert "paths" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "FastHTTP API"

    def test_generate_openapi_schema_with_tags(self) -> None:
        """Test generating OpenAPI schema with tags."""
        app = FastHTTP()

        @app.get(url="https://example.com/api/users", tags=["users"])
        async def get_users(resp: Response) -> dict:
            return resp.json()

        schema = generate_openapi_schema(app)

        # Find the path and check tags
        paths = schema["paths"]
        assert len(paths) > 0
        for path_key, path_item in paths.items():
            if "get" in path_item:
                assert path_item["get"]["tags"] == ["users"]

    def test_generate_openapi_schema_with_params(self) -> None:
        """Test generating OpenAPI schema with query parameters."""
        app = FastHTTP()

        @app.get(url="https://example.com/api/users", params={"page": "1"})
        async def get_users(resp: Response) -> dict:
            return resp.json()

        schema = generate_openapi_schema(app)

        # Check that parameters are included
        paths = schema["paths"]
        for path_key, path_item in paths.items():
            if "get" in path_item:
                assert "parameters" in path_item["get"]
                assert len(path_item["get"]["parameters"]) > 0

    def test_generate_openapi_schema_with_response_model(self) -> None:
        """Test generating OpenAPI schema with response model."""
        class UserResponse(BaseModel):
            id: int
            name: str

        app = FastHTTP()

        @app.get(url="https://example.com/api/users/1", response_model=UserResponse)
        async def get_user(resp: Response) -> UserResponse:
            return resp.json()

        schema = generate_openapi_schema(app)

        # Check that schema is included in components
        assert "components" in schema
        assert "schemas" in schema["components"]
        assert "UserResponse" in schema["components"]["schemas"]

    def test_generate_openapi_schema_multiple_routes(self) -> None:
        """Test generating OpenAPI schema with multiple routes."""
        app = FastHTTP()

        @app.get(url="https://example.com/api/users")
        async def get_users(resp: Response) -> dict:
            return resp.json()

        @app.post(url="https://example.com/api/users")
        async def create_user(resp: Response) -> dict:
            return resp.json()

        @app.put(url="https://example.com/api/users/1")
        async def update_user(resp: Response) -> dict:
            return resp.json()

        schema = generate_openapi_schema(app)

        # Should have multiple paths
        assert len(schema["paths"]) >= 2

    def test_generate_openapi_schema_with_pydantic_models(self) -> None:
        """Test generating OpenAPI schema with Pydantic request/response models."""
        class CreateUserRequest(BaseModel):
            name: str
            email: str

        class CreateUserResponse(BaseModel):
            id: int
            name: str
            email: str

        app = FastHTTP()

        @app.post(
            url="https://example.com/api/users",
            response_model=CreateUserResponse,
            request_model=CreateUserRequest,
        )
        async def create_user(resp: Response) -> CreateUserResponse:
            return resp.json()

        schema = generate_openapi_schema(app)

        # Both models should be in schemas
        schemas = schema["components"]["schemas"]
        assert "CreateUserRequest" in schemas
        assert "CreateUserResponse" in schemas

    def test_generate_openapi_schema_components_structure(self) -> None:
        """Test OpenAPI schema has correct components structure."""
        app = FastHTTP()

        @app.get(url="https://example.com/api")
        async def handler(resp: Response) -> dict:
            return {}

        schema = generate_openapi_schema(app)

        assert "components" in schema
        assert "schemas" in schema["components"]
        assert isinstance(schema["components"]["schemas"], dict)

    def test_generate_openapi_schema_info_structure(self) -> None:
        """Test OpenAPI schema has correct info structure."""
        app = FastHTTP()
        schema = generate_openapi_schema(app)

        assert "info" in schema
        assert "title" in schema["info"]
        assert "version" in schema["info"]
        assert schema["info"]["title"] == "FastHTTP API"
        assert schema["info"]["version"] == "1.0.0"
