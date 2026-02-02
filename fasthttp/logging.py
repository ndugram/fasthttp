import logging
import sys
from datetime import datetime, timezone
from typing import ClassVar

LOGGER_NAME = "fasthttp"


class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter with colored output.

    Adds ANSI colors, icons and improved formatting
    to log records based on their log level.

    Designed for CLI-friendly and readable logs.
    """
    RESET = "\033[0m"

    BOLD = "\033[1m"
    DIM = "\033[2m"

    GRAY = "\033[90m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RED = "\033[31m"
    RED_BG = "\033[41m"
    PURPLE = "\033[35m"

    LEVEL_COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: YELLOW,
        logging.INFO: GREEN,
        logging.WARNING: BLUE,
        logging.ERROR: RED,
        logging.CRITICAL: RED_BG,
    }

    LEVEL_ICONS: ClassVar[dict[int, str]] = {
        logging.DEBUG: "🐛",
        logging.INFO: "✔",
        logging.WARNING: "⚠",
        logging.ERROR: "✖",
        logging.CRITICAL: "💀",
    }

    def formatTime(self, record, datefmt=None) -> str: # noqa  N802
        """
        Format the timestamp of a log record.

        Converts the record creation time to UTC
        and formats it with millisecond precision.
        """
        t = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return f"{self.GRAY}{t.strftime('%H:%M:%S.%f')[:-3]}{self.RESET}"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record with colors and icons.

        Applies:
        - Colored log level names
        - Colored logger names
        - Emoji icons based on log level
        - Special formatting for result messages

        Returns the fully formatted log string.
        """
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        icon = self.LEVEL_ICONS.get(record.levelno, "")

        record.levelname = (
            f"{color}{self.BOLD}{record.levelname:<8}{self.RESET}"
        )
        record.name = f"{self.CYAN}{record.name}{self.RESET}"

        msg = str(record.msg)

        if msg.startswith("[RESULT]"):
            record.msg = f"{self.PURPLE}↳ {msg[8:].strip()}{self.RESET}"
        else:
            record.msg = f"{color}{icon} {msg}{self.RESET}"

        return super().format(record)


def setup_logger(*, debug: bool = False) -> logging.Logger:
    """
    Configure and return the application logger.

    Creates a logger with colored output and
    configurable verbosity based on debug mode.

    If the logger is already configured,
    returns the existing instance.
    """
    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)

    formatter = ColorFormatter(
        "%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
