import json
import sys
from typing import Any


class CLIFormatter:
    RESET = "\033[0m"

    BOLD = "\033[1m"
    DIM = "\033[2m"

    GRAY = "\033[90m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RED = "\033[31m"
    PURPLE = "\033[35m"

    SUCCESS = f"{GREEN}✔{RESET}"
    ERROR = f"{RED}✖{RESET}"
    ARROW = f"{PURPLE}↳{RESET}"

    def success(self, message: str) -> None:
        print(f"{self.SUCCESS} {message}")

    def error(self, message: str) -> None:
        print(f"{self.ERROR} {message}", file=sys.stderr)

    def info(self, message: str) -> None:
        print(f"{self.CYAN}ℹ{self.RESET} {message}")

    def result(self, label: str, value: Any) -> None:
        print(f"{self.ARROW} {self.BOLD}{label}{self.RESET}: {value}")

    def header(self, text: str) -> None:
        print(f"\n{self.CYAN}{self.BOLD}{text}{self.RESET}")
        print(f"{self.CYAN}{'─' * len(text)}{self.RESET}")

    def key_value(self, key: str, value: Any, indent: int = 0) -> None:
        prefix = " " * indent
        print(f"{prefix}{self.GRAY}{key}:{self.RESET} {value}")

    def json_output(self, data: Any) -> None:
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        print(f"{self.PURPLE}{formatted}{self.RESET}")


formatter = CLIFormatter()
