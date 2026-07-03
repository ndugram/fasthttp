"""Tests for OpenAPI schema generation."""

from enum import Enum

from pydantic import BaseModel, Field

from fasthttp import FastHTTP
from fasthttp.openapi.generator import (
    _SchemaCollector,
    _extract_docstring,
    _normalize_path,
    generate_openapi_schema,
)
from fasthttp.response import Response


class TestSchemaForType:
    """Tests for _SchemaCollector.schema_for_type (Pydantic-backed type -> schema)."""

    def test_schema_for_type_str(self) -> None:
        """Test schema for str type."""
        result = _SchemaCollector(set()).schema_for_type(str)
        assert result == {"type": "string"}

    def test_schema_for_type_int(self) -> None:
        """Test schema for int type."""
        result = _SchemaCollector(set()).schema_for_type(int)
        assert result == {"type": "integer"}

    def test_schema_for_type_float(self) -> None:
        """Test schema for float type."""
        result = _SchemaCollector(set()).schema_for_type(float)
        assert result == {"type": "number"}

    def test_schema_for_type_bool(self) -> None:
        """Test schema for bool type."""
        result = _SchemaCollector(set()).schema_for_type(bool)
        assert result == {"type": "boolean"}

    def test_schema_for_type_list(self) -> None:
        """Test schema for list type."""
        result = _SchemaCollector(set()).schema_for_type(list)
        assert result["type"] == "array"

    def test_schema_for_type_dict(self) -> None:
        """Test schema for dict type."""
        result = _SchemaCollector(set()).schema_for_type(dict)
        assert result["type"] == "object"

    def test_schema_for_type_none(self) -> None:
        """Test schema for NoneType."""
        result = _SchemaCollector(set()).schema_for_type(type(None))
        assert result == {"type": "null"}

    def test_schema_for_type_enum(self) -> None:
        """Enums resolve to a proper `enum` list instead of a plain string."""

        class Color(str, Enum):
            red = "red"
            blue = "blue"

        result = _SchemaCollector(set()).schema_for_type(Color)
        assert result["enum"] == ["red", "blue"]

    def test_schema_for_type_optional(self) -> None:
        """Optional/Union types resolve via anyOf instead of falling back to string."""
        result = _SchemaCollector(set()).schema_for_type(int | None)
        types = {branch.get("type") for branch in result["anyOf"]}
        assert types == {"integer", "null"}


class TestExtractDocstring:
    """Tests for _extract_docstring function."""

    def test_extract_docstring_basic(self) -> None:
        """Test extracting docstring from function."""

        def example_func():
            """This is a test function."""

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

        result = _extract_docstring(multiline_func)
        assert "multiline" in result
        assert "docstring" in result


class TestModelJsonSchema:
    """Tests for _SchemaCollector's model schema generation (backed by model_json_schema)."""

    def test_generate_schema_basic_model(self) -> None:
        """Test generating schema from basic Pydantic model."""

        class UserModel(BaseModel):
            name: str
            age: int

        collector = _SchemaCollector({UserModel})
        result = collector.schemas["UserModel"]

        assert result["type"] == "object"
        assert "name" in result["properties"]
        assert "age" in result["properties"]
        assert "name" in result["required"]
        assert "age" in result["required"]

    def test_generate_schema_with_optional_fields(self) -> None:
        """Test generating schema with optional fields."""

        class OptionalModel(BaseModel):
            required_field: str
            optional_field: str | None = None

        collector = _SchemaCollector({OptionalModel})
        result = collector.schemas["OptionalModel"]

        assert "required_field" in result["required"]
        # optional_field should not be in required list
        assert "optional_field" not in result.get("required", [])

    def test_generate_schema_with_field_description(self) -> None:
        """Descriptions from `Field(description=...)` are preserved via Pydantic."""

        class DescribedModel(BaseModel):
            name: str = Field(description="the user's name")

        collector = _SchemaCollector({DescribedModel})
        result = collector.schemas["DescribedModel"]

        assert result["properties"]["name"]["description"] == "the user's name"

    def test_generate_schema_with_enum_field(self) -> None:
        """Enum fields resolve to a shared $ref + enum values, not a plain string."""

        class Role(str, Enum):
            admin = "admin"
            user = "user"

        class Account(BaseModel):
            role: Role

        collector = _SchemaCollector({Account})

        assert collector.schemas["Role"]["enum"] == ["admin", "user"]
        assert collector.schemas["Account"]["properties"]["role"] == {
            "$ref": "#/components/schemas/Role"
        }

    def test_generate_schema_with_nested_model(self) -> None:
        """Nested models are discovered automatically and added to components/schemas."""

        class Address(BaseModel):
            city: str

        class Person(BaseModel):
            name: str
            address: Address

        collector = _SchemaCollector({Person})

        assert "Address" in collector.schemas
        assert collector.schemas["Person"]["properties"]["address"] == {
            "$ref": "#/components/schemas/Address"
        }


class TestSchemaForValue:
    """Tests for _SchemaCollector.schema_for_value (used for query params & raw bodies)."""

    def test_schema_for_value_scalar(self) -> None:
        """Test generating schema from a scalar value."""
        result = _SchemaCollector(set()).schema_for_value("1")
        assert result == {"type": "string"}

    def test_schema_for_value_dict(self) -> None:
        """Test generating schema from a dict value."""
        result = _SchemaCollector(set()).schema_for_value({"page": 1, "limit": 10})

        assert result["type"] == "object"
        assert result["properties"]["page"] == {"type": "integer"}
        assert result["properties"]["limit"] == {"type": "integer"}


class TestResponseSchema:
    """Tests for _SchemaCollector.response_schema."""

    def test_generate_response_schema_none(self) -> None:
        """Test generating response schema without model."""
        result = _SchemaCollector(set()).response_schema(None)

        assert result["description"] == "Successful response"

    def test_generate_response_schema_with_model(self) -> None:
        """Test generating response schema with Pydantic model."""

        class ResponseModel(BaseModel):
            id: int
            name: str

        result = _SchemaCollector({ResponseModel}).response_schema(ResponseModel)

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
        for _, path_item in paths.items():
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
        for _, path_item in paths.items():
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
        async def handler(_resp: Response) -> dict:
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

    def test_generate_openapi_schema_with_server_url(self) -> None:
        """Test generating OpenAPI schema with Swagger proxy server URL."""
        app = FastHTTP()

        @app.get(url="https://example.com/api")
        async def handler(_resp: Response) -> dict:
            return {}

        schema = generate_openapi_schema(app, server_url="/api/request")

        assert schema["servers"] == [
            {
                "url": "/api/request",
                "description": "FastHTTP Proxy",
            }
        ]
