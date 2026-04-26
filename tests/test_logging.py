"""Tests for ColorFormatter and setup_logger."""
import logging
import pytest

from fasthttp.logging import ColorFormatter, setup_logger, LOGGER_NAME


class TestColorFormatter:
    def test_format_debug(self):
        formatter = ColorFormatter("%(levelname)s %(message)s")
        record = logging.LogRecord(
            name="test", level=logging.DEBUG,
            pathname="", lineno=0, msg="debug msg",
            args=(), exc_info=None,
        )
        result = formatter.format(record)
        assert "debug msg" in result

    def test_format_info(self):
        formatter = ColorFormatter("%(levelname)s %(message)s")
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="info msg",
            args=(), exc_info=None,
        )
        result = formatter.format(record)
        assert "info msg" in result

    def test_format_warning(self):
        formatter = ColorFormatter("%(levelname)s %(message)s")
        record = logging.LogRecord(
            name="test", level=logging.WARNING,
            pathname="", lineno=0, msg="warn msg",
            args=(), exc_info=None,
        )
        result = formatter.format(record)
        assert "warn msg" in result

    def test_format_error(self):
        formatter = ColorFormatter("%(levelname)s %(message)s")
        record = logging.LogRecord(
            name="test", level=logging.ERROR,
            pathname="", lineno=0, msg="error msg",
            args=(), exc_info=None,
        )
        result = formatter.format(record)
        assert "error msg" in result

    def test_format_critical(self):
        formatter = ColorFormatter("%(levelname)s %(message)s")
        record = logging.LogRecord(
            name="test", level=logging.CRITICAL,
            pathname="", lineno=0, msg="critical msg",
            args=(), exc_info=None,
        )
        result = formatter.format(record)
        assert "critical msg" in result

    def test_format_result_prefix(self):
        formatter = ColorFormatter("%(message)s")
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="[RESULT] done",
            args=(), exc_info=None,
        )
        result = formatter.format(record)
        assert "done" in result

    def test_format_time_returns_string(self):
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="x",
            args=(), exc_info=None,
        )
        ts = formatter.formatTime(record)
        assert isinstance(ts, str)
        assert ":" in ts

    def test_level_colors_defined_for_all_standard_levels(self):
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            assert level in ColorFormatter.LEVEL_COLORS

    def test_level_icons_defined_for_all_standard_levels(self):
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            assert level in ColorFormatter.LEVEL_ICONS

    def test_levelname_contains_ansi_reset(self):
        formatter = ColorFormatter("%(levelname)s")
        record = logging.LogRecord(
            name="test", level=logging.DEBUG,
            pathname="", lineno=0, msg="x",
            args=(), exc_info=None,
        )
        formatter.format(record)
        assert "\033[0m" in record.levelname

    def test_unknown_level_uses_reset_color(self):
        formatter = ColorFormatter("%(message)s")
        record = logging.LogRecord(
            name="test", level=99,
            pathname="", lineno=0, msg="custom level",
            args=(), exc_info=None,
        )
        result = formatter.format(record)
        assert "custom level" in result


class TestSetupLogger:
    def setup_method(self):
        logger = logging.getLogger(LOGGER_NAME)
        logger.handlers.clear()

    def test_returns_logger(self):
        logger = setup_logger()
        assert isinstance(logger, logging.Logger)

    def test_logger_name(self):
        logger = setup_logger()
        assert logger.name == LOGGER_NAME

    def test_logger_has_handler(self):
        logger = setup_logger()
        assert len(logger.handlers) >= 1

    def test_logger_does_not_propagate(self):
        logger = setup_logger()
        assert logger.propagate is False

    def test_second_call_returns_same_logger(self):
        logger1 = setup_logger()
        handler_count = len(logger1.handlers)
        logger2 = setup_logger()
        assert logger1 is logger2
        assert len(logger2.handlers) == handler_count

    def test_debug_mode_sets_handler_level(self):
        logger = setup_logger(debug=True)
        handler = logger.handlers[0]
        assert handler.level == logging.DEBUG

    def test_non_debug_sets_info_level(self):
        logger = setup_logger(debug=False)
        handler = logger.handlers[0]
        assert handler.level == logging.INFO

    def test_handler_has_color_formatter(self):
        logger = setup_logger()
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, ColorFormatter)
