import pytest

from fasthttp.cli.codegen import (
    CodegenError,
    collect_models,
    generate_client,
    generate_model,
    generate_operation,
    load_spec,
    python_type,
)

PETSTORE_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Petstore Test API", "version": "1.0.0"},
    "servers": [{"url": "https://api.petstore.example.com"}],
    "paths": {
        "/pets": {
            "get": {
                "operationId": "listPets",
                "summary": "List all pets",
                "tags": ["pets"],
                "parameters": [{"name": "limit", "in": "query", "schema": {"type": "integer"}}],
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/PetList"}}
                        },
                    }
                },
            },
            "post": {
                "operationId": "createPet",
                "summary": "Create a pet",
                "tags": ["pets"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/NewPet"}}
                    }
                },
                "responses": {
                    "201": {
                        "description": "Created",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Pet"}}
                        },
                    }
                },
            },
        },
        "/pets/{petId}": {
            "get": {
                "operationId": "getPet",
                "summary": "Get a pet by id",
                "tags": ["pets"],
                "parameters": [
                    {"name": "petId", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Pet"}}
                        },
                    }
                },
            }
        },
    },
    "components": {
        "schemas": {
            "NewPet": {
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string"}, "tag": {"type": "string"}},
            },
            "Pet": {
                "type": "object",
                "required": ["id", "name"],
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "tag": {"type": "string"},
                    "status": {"type": "string", "enum": ["available", "pending", "sold"]},
                },
            },
            "PetList": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"$ref": "#/components/schemas/Pet"}}
                },
            },
        }
    },
}


class TestLoadSpec:
    def test_load_json_file(self, tmp_path):
        import orjson

        spec_path = tmp_path / "spec.json"
        spec_path.write_bytes(orjson.dumps(PETSTORE_SPEC))

        loaded = load_spec(str(spec_path))

        assert loaded["info"]["title"] == "Petstore Test API"

    def test_load_missing_file_raises(self):
        with pytest.raises(CodegenError, match="not found"):
            load_spec("/no/such/spec.json")


class TestPythonType:
    def test_string(self):
        assert python_type({"type": "string"}) == "str"

    def test_integer(self):
        assert python_type({"type": "integer"}) == "int"

    def test_optional(self):
        assert python_type({"type": "string"}, required=False) == "str | None"

    def test_ref(self):
        assert python_type({"$ref": "#/components/schemas/Pet"}) == "Pet"

    def test_array_of_ref(self):
        assert python_type({"type": "array", "items": {"$ref": "#/components/schemas/Pet"}}) == "list[Pet]"

    def test_enum(self):
        assert (
            python_type({"type": "string", "enum": ["a", "b"]})
            == "Literal['a', 'b']"
        )

    def test_composed_schema_falls_back_to_any(self):
        assert python_type({"oneOf": [{"type": "string"}, {"type": "integer"}]}) == "Any"

    def test_empty_schema(self):
        assert python_type(None) == "Any"


class TestGenerateModel:
    def test_generates_pydantic_class(self):
        code = generate_model("Pet", PETSTORE_SPEC["components"]["schemas"]["Pet"])
        assert "class Pet(BaseModel):" in code
        assert "id: int" in code
        assert "name: str" in code
        assert "tag: str | None = None" in code

    def test_no_properties(self):
        code = generate_model("Empty", {"type": "object"})
        assert code == "class Empty(BaseModel):\n    pass"


class TestCollectModels:
    def test_collects_all_named_schemas(self):
        models = collect_models(PETSTORE_SPEC)
        assert len(models) == 3
        assert any("class Pet(BaseModel):" in m for m in models)
        assert any("class NewPet(BaseModel):" in m for m in models)
        assert any("class PetList(BaseModel):" in m for m in models)


class TestGenerateOperation:
    def test_no_path_params_generates_decorated_route(self):
        op = PETSTORE_SPEC["paths"]["/pets"]["get"]
        code = generate_operation("/pets", "get", op)
        assert code.startswith("@app.get(")
        assert 'url="/pets"' in code
        assert "response_model=PetList" in code
        assert "async def list_pets(resp: Response) -> dict:" in code

    def test_post_with_body_model(self):
        op = PETSTORE_SPEC["paths"]["/pets"]["post"]
        code = generate_operation("/pets", "post", op)
        assert "async def create_pet(resp: Response, body: NewPet) -> dict:" in code
        assert 'body.model_dump(mode="json"' in code

    def test_path_params_generates_imperative_function(self):
        op = PETSTORE_SPEC["paths"]["/pets/{petId}"]["get"]
        code = generate_operation("/pets/{petId}", "get", op)
        assert not code.startswith("@app.")
        assert "async def get_pet(session: AsyncSession, petId: str) -> dict | None:" in code
        assert 'f"{base_url}/pets/{petId}"' in code


class TestGenerateClient:
    def test_full_spec_produces_valid_python(self):
        code = generate_client(PETSTORE_SPEC)
        compile(code, "<generated>", "exec")

    def test_contains_expected_pieces(self):
        code = generate_client(PETSTORE_SPEC)
        assert 'base_url = "https://api.petstore.example.com"' in code
        assert "class Pet(BaseModel):" in code
        assert '@app.get(url="/pets"' in code
        assert "async def get_pet(session: AsyncSession" in code

    def test_generated_client_is_importable_and_routes_registered(self, tmp_path):
        code = generate_client(PETSTORE_SPEC)
        module_path = tmp_path / "generated.py"
        module_path.write_text(code)

        import importlib.util

        spec = importlib.util.spec_from_file_location("generated_test_client", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert len(module.app.routes) == 2
        assert {r.url for r in module.app.routes} == {
            "https://api.petstore.example.com/pets",
        }
        pet = module.Pet(id=1, name="Rex", status="available")
        assert pet.status == "available"
