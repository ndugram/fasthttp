import pytest
import logging

from fasthttp.exceptions import (
    FastHTTPBadStatusError,
    FastHTTPConnectionError,
    FastHTTPRequestError,
    FastHTTPTimeoutError,
    FastHTTPValidationError,
    log_success,
)
from fasthttp.exceptions.base import FastHTTPError
from fasthttp.exceptions.types import colorize, handle_error


class TestExceptions:
    """Tests for FastHTTP exception classes."""

    def test_bad_status_error_creation(self) -> None:
        """Test FastHTTPBadStatusError creation."""
        error = FastHTTPBadStatusError(
            message="404 Not Found",
            url="http://example.com/notfound",
            method="GET",
            status_code=404,
        )

        assert error.message == "404 Not Found"
        assert error.url == "http://example.com/notfound"
        assert error.method == "GET"
        assert error.status_code == 404

    def test_bad_status_error_auto_message(self) -> None:
        """Test that status code generates message if not provided."""
        error = FastHTTPBadStatusError(status_code=500)

        assert error.message == "HTTP 500"

    def test_bad_status_error_body_preview(self) -> None:
        """Test that response body is truncated in details."""
        long_body = "x" * 150
        error = FastHTTPBadStatusError(
            message="Error",
            response_body=long_body,
        )

        assert "body_preview" in error.details
        assert len(error.details["body_preview"]) == 103  # 100 + "..."

    def test_connection_error_creation(self) -> None:
        """Test FastHTTPConnectionError creation."""
        error = FastHTTPConnectionError(
            message="Connection failed",
            url="http://example.com",
            method="GET",
        )

        assert error.message == "Connection failed"
        assert error.url == "http://example.com"
        assert error.method == "GET"

    def test_timeout_error_creation(self) -> None:
        """Test FastHTTPTimeoutError creation."""
        error = FastHTTPTimeoutError(
            message="Request timed out",
            url="http://example.com/slow",
            method="GET",
            timeout=30.0,
        )

        assert error.message == "Request timed out"
        assert error.details.get("timeout") == 30.0

    def test_request_error_creation(self) -> None:
        """Test FastHTTPRequestError creation."""
        error = FastHTTPRequestError(
            message="Unknown error occurred",
            url="http://example.com",
            method="POST",
        )

        assert error.message == "Unknown error occurred"

    def test_validation_error_creation(self) -> None:
        """Test FastHTTPValidationError creation."""
        error = FastHTTPValidationError(
            message="Invalid parameter",
            details={"field": "email"},
        )

        assert error.message == "Invalid parameter"
        assert error.details.get("field") == "email"

    def test_validation_error_with_value(self) -> None:
        """Test FastHTTPValidationError with invalid value."""
        error = FastHTTPValidationError(
            message="Invalid email format",
            details={"field": "email", "value": "not-an-email"},
        )

        assert error.details.get("value") == "not-an-email"

    def test_error_log_method(self) -> None:
        """Test that errors can log themselves."""
        error = FastHTTPBadStatusError(
            message="Error",
            url="http://example.com",
            method="GET",
            status_code=400,
        )

        # Just verify it doesn't crash
        error.log()
        assert True


class TestLogSuccess:
    """Tests for the log_success function."""

    def test_log_success_calls_logger(self) -> None:
        """Test that log_success logs successful requests."""
        # Just verify it doesn't crash
        log_success("http://example.com", "GET", 200, 50.5)
        assert True

    def test_log_success_includes_timing(self) -> None:
        """Test that log_success includes elapsed time."""
        # Just verify it doesn't crash
        log_success("http://example.com", "GET", 200, 100.0)
        assert True


class TestFastHTTPErrorBase:
    def test_is_exception_subclass(self):
        assert issubclass(FastHTTPError, Exception)

    def test_str_contains_message(self):
        err = FastHTTPError("something broke")
        assert "something broke" in str(err)

    def test_str_contains_url(self):
        err = FastHTTPError("oops", url="https://x.com")
        assert "https://x.com" in str(err)

    def test_str_contains_method(self):
        err = FastHTTPError("oops", method="DELETE")
        assert "DELETE" in str(err)

    def test_str_contains_status(self):
        err = FastHTTPError("oops", status_code=503)
        assert "503" in str(err)

    def test_details_default_empty_dict(self):
        err = FastHTTPError("oops")
        assert err.details == {}

    def test_details_stored(self):
        err = FastHTTPError("oops", details={"key": "val"})
        assert err.details["key"] == "val"

    def test_details_none_becomes_empty(self):
        err = FastHTTPError("oops", details=None)
        assert err.details == {}

    def test_str_contains_details(self):
        err = FastHTTPError("oops", details={"foo": "bar"})
        assert "foo" in str(err)

    def test_log_does_not_raise(self):
        err = FastHTTPError("oops", url="u", method="GET", status_code=500)
        err.log()

    def test_log_with_custom_level(self):
        err = FastHTTPError("oops")
        err.log(level=logging.WARNING)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(FastHTTPError):
            raise FastHTTPError("test raise")


class TestFastHTTPBadStatusErrorExtended:
    def test_default_message_no_status(self):
        err = FastHTTPBadStatusError()
        assert err.message == "Bad status"

    def test_short_body_not_truncated(self):
        err = FastHTTPBadStatusError(response_body="short")
        assert err.details["body_preview"] == "short"

    def test_exactly_100_chars_not_truncated(self):
        body = "x" * 100
        err = FastHTTPBadStatusError(response_body=body)
        assert err.details["body_preview"] == body
        assert not err.details["body_preview"].endswith("...")

    def test_101_chars_truncated(self):
        body = "x" * 101
        err = FastHTTPBadStatusError(response_body=body)
        assert err.details["body_preview"].endswith("...")

    def test_is_subclass_of_base(self):
        assert issubclass(FastHTTPBadStatusError, FastHTTPError)

    def test_can_be_raised(self):
        with pytest.raises(FastHTTPBadStatusError):
            raise FastHTTPBadStatusError(status_code=404)


class TestFastHTTPTimeoutErrorExtended:
    def test_default_message(self):
        err = FastHTTPTimeoutError()
        assert err.message == "Request timed out"

    def test_no_timeout_no_details(self):
        err = FastHTTPTimeoutError()
        assert "timeout" not in err.details

    def test_timeout_stored_in_details(self):
        err = FastHTTPTimeoutError(timeout=30)
        assert err.details["timeout"] == 30

    def test_is_subclass_of_base(self):
        assert issubclass(FastHTTPTimeoutError, FastHTTPError)


class TestFastHTTPConnectionErrorExtended:
    def test_default_message(self):
        err = FastHTTPConnectionError()
        assert err.message == "Connection failed"

    def test_is_subclass_of_base(self):
        assert issubclass(FastHTTPConnectionError, FastHTTPError)

    def test_can_be_raised(self):
        with pytest.raises(FastHTTPConnectionError):
            raise FastHTTPConnectionError(url="https://x.com")


class TestFastHTTPValidationErrorExtended:
    def test_default_message(self):
        err = FastHTTPValidationError()
        assert err.message == "Validation failed"

    def test_is_subclass_of_base(self):
        assert issubclass(FastHTTPValidationError, FastHTTPError)


class TestFastHTTPRequestErrorExtended:
    def test_is_subclass_of_base(self):
        assert issubclass(FastHTTPRequestError, FastHTTPError)

    def test_can_be_raised(self):
        with pytest.raises(FastHTTPRequestError):
            raise FastHTTPRequestError("bad request")


class TestColorize:
    def test_colorize_returns_string(self):
        result = colorize("hello", "red")
        assert isinstance(result, str)

    def test_colorize_contains_original_text(self):
        result = colorize("world", "blue")
        assert "world" in result

    def test_colorize_contains_reset(self):
        result = colorize("text", "green")
        assert "\033[0m" in result

    def test_colorize_unknown_color_no_crash(self):
        result = colorize("text", "purple_unicorn")
        assert "text" in result


class TestHandleError:
    def test_handle_error_raises_by_default(self):
        err = FastHTTPError("boom")
        with pytest.raises(FastHTTPError):
            handle_error(err)

    def test_handle_error_no_raise(self):
        err = FastHTTPError("boom")
        handle_error(err, raise_it=False)

    def test_handle_error_raises_correct_type(self):
        err = FastHTTPBadStatusError(status_code=500)
        with pytest.raises(FastHTTPBadStatusError):
            handle_error(err)
