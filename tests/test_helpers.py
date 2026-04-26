"""Tests for helpers/route_inspect.py."""
import inspect
import pytest
from pydantic import BaseModel

from fasthttp.helpers.route_inspect import (
    check_annotated_parameters,
    check_annotated_return,
    validate_handler,
    create_route_params,
    COMMON_PARAMS,
)


# ---------------------------------------------------------------------------
# check_annotated_parameters
# ---------------------------------------------------------------------------

class TestCheckAnnotatedParameters:
    def test_fully_annotated_passes(self):
        def fn(x: int, y: str) -> None:
            pass
        check_annotated_parameters(func=fn)

    def test_no_params_passes(self):
        def fn() -> None:
            pass
        check_annotated_parameters(func=fn)

    def test_missing_annotation_raises(self):
        def fn(x) -> None:
            pass
        with pytest.raises(TypeError, match="x"):
            check_annotated_parameters(func=fn)

    def test_partial_annotation_raises(self):
        def fn(x: int, y) -> None:
            pass
        with pytest.raises(TypeError, match="y"):
            check_annotated_parameters(func=fn)

    def test_error_message_contains_function_name(self):
        def my_func(unannotated) -> None:
            pass
        with pytest.raises(TypeError, match="my_func"):
            check_annotated_parameters(func=my_func)

    def test_async_func_passes(self):
        async def fn(x: int) -> None:
            pass
        check_annotated_parameters(func=fn)


# ---------------------------------------------------------------------------
# check_annotated_return
# ---------------------------------------------------------------------------

class TestCheckAnnotatedReturn:
    def test_annotated_return_passes(self):
        def fn() -> int:
            return 1
        check_annotated_return(func=fn)

    def test_none_return_passes(self):
        def fn() -> None:
            pass
        check_annotated_return(func=fn)

    def test_missing_return_raises(self):
        def fn():
            pass
        with pytest.raises(TypeError, match="return type"):
            check_annotated_return(func=fn)

    def test_error_message_contains_function_name(self):
        def my_handler():
            pass
        with pytest.raises(TypeError, match="my_handler"):
            check_annotated_return(func=my_handler)

    def test_complex_return_type_passes(self):
        def fn() -> dict[str, list[int]]:
            return {}
        check_annotated_return(func=fn)


# ---------------------------------------------------------------------------
# validate_handler
# ---------------------------------------------------------------------------

class TestValidateHandler:
    def test_valid_handler_passes(self):
        def fn(x: int, y: str) -> bool:
            return True
        validate_handler(fn)

    def test_missing_param_annotation_raises(self):
        def fn(x) -> bool:
            return True
        with pytest.raises(TypeError):
            validate_handler(fn)

    def test_missing_return_annotation_raises(self):
        def fn(x: int):
            pass
        with pytest.raises(TypeError):
            validate_handler(fn)

    def test_both_missing_raises(self):
        def fn(x):
            pass
        with pytest.raises(TypeError):
            validate_handler(fn)

    def test_async_valid_handler_passes(self):
        async def fn(x: int) -> str:
            return str(x)
        validate_handler(fn)


# ---------------------------------------------------------------------------
# create_route_params
# ---------------------------------------------------------------------------

class TestCreateRouteParams:
    def test_minimal_returns_dict(self):
        result = create_route_params(method="GET", url="https://example.com")
        assert isinstance(result, dict)
        assert result["method"] == "GET"
        assert result["url"] == "https://example.com"

    def test_defaults(self):
        result = create_route_params(method="POST", url="https://example.com")
        assert result["params"] is None
        assert result["json"] is None
        assert result["data"] is None
        assert result["response_model"] is None
        assert result["request_model"] is None
        assert result["tags"] == []
        assert result["dependencies"] == []
        assert result["skip_request"] is False
        assert result["responses"] == {}

    def test_none_tags_becomes_empty_list(self):
        result = create_route_params(method="GET", url="u", tags=None)
        assert result["tags"] == []

    def test_none_dependencies_becomes_empty_list(self):
        result = create_route_params(method="GET", url="u", dependencies=None)
        assert result["dependencies"] == []

    def test_none_responses_becomes_empty_dict(self):
        result = create_route_params(method="GET", url="u", responses=None)
        assert result["responses"] == {}

    def test_params_forwarded(self):
        result = create_route_params(method="GET", url="u", params={"q": "1"})
        assert result["params"] == {"q": "1"}

    def test_json_forwarded(self):
        result = create_route_params(method="POST", url="u", json={"a": 1})
        assert result["json"] == {"a": 1}

    def test_data_forwarded(self):
        result = create_route_params(method="POST", url="u", data=b"bytes")
        assert result["data"] == b"bytes"

    def test_skip_request_forwarded(self):
        result = create_route_params(method="GET", url="u", skip_request=True)
        assert result["skip_request"] is True

    def test_response_model_forwarded(self):
        class M(BaseModel):
            x: int
        result = create_route_params(method="GET", url="u", response_model=M)
        assert result["response_model"] is M

    def test_request_model_forwarded(self):
        class M(BaseModel):
            x: int
        result = create_route_params(method="POST", url="u", request_model=M)
        assert result["request_model"] is M

    def test_tags_forwarded(self):
        result = create_route_params(method="GET", url="u", tags=["a", "b"])
        assert result["tags"] == ["a", "b"]

    def test_all_http_methods(self):
        for m in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            result = create_route_params(method=m, url="u")
            assert result["method"] == m


# ---------------------------------------------------------------------------
# COMMON_PARAMS
# ---------------------------------------------------------------------------

class TestCommonParams:
    def test_common_params_exists(self):
        assert COMMON_PARAMS is not None

    def test_response_model_key(self):
        assert "response_model" in COMMON_PARAMS

    def test_request_model_key(self):
        assert "request_model" in COMMON_PARAMS

    def test_tags_key(self):
        assert "tags" in COMMON_PARAMS

    def test_dependencies_key(self):
        assert "dependencies" in COMMON_PARAMS

    def test_responses_key(self):
        assert "responses" in COMMON_PARAMS

    def test_each_entry_has_type(self):
        for key, val in COMMON_PARAMS.items():
            assert "type" in val, f"{key} missing 'type'"

    def test_each_entry_has_default(self):
        for key, val in COMMON_PARAMS.items():
            assert "default" in val, f"{key} missing 'default'"
