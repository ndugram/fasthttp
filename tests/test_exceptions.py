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

    def test_error_log_method(self, caplog) -> None:
        """Test that errors can log themselves."""
        error = FastHTTPBadStatusError(
            message="Error",
            url="http://example.com",
            method="GET",
            status_code=400,
        )

        with caplog.at_level(logging.DEBUG):
            error.log()

        assert len(caplog.records) > 0


class TestLogSuccess:
    """Tests for the log_success function."""

    def test_log_success_calls_logger(self, caplog) -> None:
        """Test that log_success logs successful requests."""
        with caplog.at_level(logging.DEBUG):
            log_success("http://example.com", "GET", 200, 50.5)

        assert len(caplog.records) > 0

    def test_log_success_includes_timing(self, caplog) -> None:
        """Test that log_success includes elapsed time."""
        with caplog.at_level(logging.DEBUG):
            log_success("http://example.com", "GET", 200, 100.0)

        log_text = caplog.text
        assert "100.0ms" in log_text or "100" in log_text
