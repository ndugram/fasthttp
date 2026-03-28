import asyncio
import json
import shlex
from typing import Any

import httpx


try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    PROMPT_METHOD = BRIGHT_CYAN
    PROMPT_URL = BRIGHT_GREEN
    PROMPT_ARROW = BRIGHT_YELLOW

    STATUS_2XX = BRIGHT_GREEN
    STATUS_3XX = BRIGHT_YELLOW
    STATUS_4XX = BRIGHT_RED
    STATUS_5XX = BRIGHT_RED + BOLD


class FastHTTPRepl:
    """Interactive REPL for FastHTTP."""

    def __init__(self, proxy: str | None = None) -> None:
        self.proxy = proxy
        self.client = httpx.AsyncClient(proxy=proxy, timeout=30.0)
        self.history: list[str] = []
        self.last_response: dict[str, Any] | None = None

    METHOD_COLORS = {
        "get": Colors.BRIGHT_GREEN,
        "post": Colors.BRIGHT_YELLOW,
        "put": Colors.BRIGHT_BLUE,
        "patch": Colors.BRIGHT_MAGENTA,
        "delete": Colors.BRIGHT_RED,
        "head": Colors.BRIGHT_CYAN,
        "options": Colors.BRIGHT_WHITE,
        "g": Colors.BRIGHT_GREEN,
        "p": Colors.BRIGHT_YELLOW,
        "pu": Colors.BRIGHT_BLUE,
        "pa": Colors.BRIGHT_MAGENTA,
        "d": Colors.BRIGHT_RED,
    }

    def _check_https_url(self, url: str) -> str:
        url = url.strip()
        if url.startswith(("https://", "http://")):
            return url
        return f"https://{url}"

    def print_banner(self) -> None:
        """Print welcome message."""
        print(f"{Colors.BRIGHT_CYAN}FastHTTP Interactive{Colors.RESET} - {Colors.DIM}Type help for commands{Colors.RESET}")
        print()

    def get_method_color(self, method: str) -> str:
        """Get color for HTTP method."""
        return self.METHOD_COLORS.get(method.lower(), Colors.BRIGHT_CYAN)

    def print_help(self) -> None:
        """Print help message."""
        help_text = f"""
{Colors.BOLD}Available Commands:{Colors.RESET}

  {Colors.CYAN}<METHOD> <URL> [OPTIONS]{Colors.RESET}
    {Colors.DIM}Make HTTP request{Colors.RESET}
    {Colors.BRIGHT_GREEN}get{Colors.RESET}    https://api.example.com/data
    {Colors.BRIGHT_YELLOW}post{Colors.RESET}   https://api.example.com/users --json '{{"name": "John"}}'
    {Colors.BRIGHT_BLUE}put{Colors.RESET}     https://api.example.com/users/1 --json '{{"name": "Jane"}}'
    {Colors.BRIGHT_MAGENTA}patch{Colors.RESET}  https://api.example.com/users/1 --json '{{"age": 25}}'
    {Colors.BRIGHT_RED}delete{Colors.RESET}  httrps://api.example.com/users/1

  {Colors.CYAN}Options:{Colors.RESET}
    -H, --header <key:value>   Add header
    -j, --json <json>          JSON body
    -d, --data <data>          Form data
    -t, --timeout <seconds>    Request timeout
    -o, --output <format>      Output format (json/text/status/headers/all)
    -p, --proxy <url>          Proxy URL (http://, https://, socks5://)

  {Colors.CYAN}Special Commands:{Colors.RESET}
    {Colors.BRIGHT_GREEN}help{Colors.RESET}     - Show this help
    {Colors.BRIGHT_GREEN}history{Colors.RESET}  - Show command history
    {Colors.BRIGHT_GREEN}last{Colors.RESET}     - Show last response
    {Colors.BRIGHT_GREEN}clear{Colors.RESET}    - Clear screen
    {Colors.BRIGHT_GREEN}exit{Colors.RESET}     - Exit REPL

  {Colors.CYAN}Shortcuts:{Colors.RESET}
    {Colors.BRIGHT_CYAN}g{Colors.RESET} <url>    - GET request
    {Colors.BRIGHT_YELLOW}p{Colors.RESET} <url>    - POST request
    {Colors.BRIGHT_CYAN}q{Colors.RESET}           - Exit (shortcut)

  {Colors.CYAN}Examples:{Colors.RESET}
    {Colors.DIM}get https://jsonplaceholder.typicode.com/posts/1{Colors.RESET}
    {Colors.DIM}post https://api.example.com/users -j '{{"name": "John"}}'{Colors.RESET}
    {Colors.DIM}g https://httpbin.org/headers -H 'Authorization: Bearer token'{Colors.RESET}
"""
        print(help_text)

    def get_prompt(self) -> str:
        """Get the prompt string."""
        return f"{Colors.GREEN}>>> {Colors.RESET}"

    def parse_command(self, line: str) -> tuple[str, list[str]]:
        """Parse command line into method and args."""
        try:
            parts = shlex.split(line)
        except ValueError:
            parts = line.split()

        if not parts:
            return "", []

        return parts[0].lower(), parts[1:]

    def parse_args(self, args: list[str]) -> dict[str, Any]:
        """Parse arguments into options."""
        result = {
            "url": None,
            "headers": {},
            "json": None,
            "data": None,
            "timeout": 30.0,
            "output": "json",
            "proxy": None,
        }

        i = 0
        while i < len(args):
            arg = args[i]

            if arg in ("-H", "--header") and i + 1 < len(args):
                header = args[i + 1]
                if ":" in header:
                    key, value = header.split(":", 1)
                    result["headers"][key.strip()] = value.strip()
                i += 2
            elif arg in ("-j", "--json") and i + 1 < len(args):
                try:
                    result["json"] = json.loads(args[i + 1])
                except json.JSONDecodeError:
                    print(f"{Colors.RED}Invalid JSON: {args[i + 1]}{Colors.RESET}")
                i += 2
            elif arg in ("-d", "--data") and i + 1 < len(args):
                result["data"] = args[i + 1]
                i += 2
            elif arg in ("-t", "--timeout") and i + 1 < len(args):
                try:
                    result["timeout"] = float(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif arg in ("-o", "--output") and i + 1 < len(args):
                result["output"] = args[i + 1]
                i += 2
            elif arg in ("-p", "--proxy") and i + 1 < len(args):
                result["proxy"] = args[i + 1]
                i += 2
            elif not arg.startswith("-"):
                result["url"] = arg
                i += 1
            else:
                i += 1

        return result

    def get_status_color(self, status: int) -> str:
        """Get color for HTTP status code."""
        if 200 <= status < 300:
            return Colors.STATUS_2XX
        elif 300 <= status < 400:
            return Colors.STATUS_3XX
        elif 400 <= status < 500:
            return Colors.STATUS_4XX
        else:
            return Colors.STATUS_5XX

    def format_output(self, resp: httpx.Response, output_format: str) -> str:
        """Format response based on output format."""
        elapsed_ms = resp.elapsed.total_seconds() * 1000

        status_color = self.get_status_color(resp.status_code)
        status_str = f"{status_color}{resp.status_code}{Colors.RESET}"

        header = f"{Colors.BRIGHT_WHITE}HTTP {status_str}{Colors.RESET} in {Colors.BRIGHT_CYAN}{elapsed_ms:.2f}ms{Colors.RESET}"

        match output_format.lower():
            case "status":
                return str(resp.status_code)
            case "headers":
                return json.dumps(dict(resp.headers), indent=2, ensure_ascii=False)
            case "json":
                try:
                    return json.dumps(resp.json(), indent=2, ensure_ascii=False)
                except Exception:
                    return resp.text
            case "text":
                return resp.text
            case "all":
                return f"""{header}

{Colors.BRIGHT_WHITE}Headers:{Colors.RESET}
{json.dumps(dict(resp.headers), indent=2, ensure_ascii=False)}

{Colors.BRIGHT_WHITE}Body:{Colors.RESET}
{resp.text[:1000]}"""
            case _:
                try:
                    return json.dumps(resp.json(), indent=2, ensure_ascii=False)
                except Exception:
                    return resp.text

    async def execute_request(self, method: str, url: str, **kwargs) -> httpx.Response | None:
        """Execute HTTP request."""
        proxy = kwargs.get("proxy", self.proxy)
        
        try:
            async with httpx.AsyncClient(proxy=proxy, timeout=kwargs.get("timeout", 30.0)) as client:
                resp = await client.request(
                    method=method,
                    url=url,
                    headers=kwargs.get("headers"),
                    json=kwargs.get("json"),
                    content=kwargs.get("data"),
                )
            return resp
        except httpx.ConnectError as e:
            print(f"{Colors.RED}Connection failed: {e}{Colors.RESET}")
            return None
        except httpx.TimeoutException as e:
            print(f"{Colors.RED}Request timed out: {e}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            return None

    async def run_command(self, command: str):
        """Run a single command."""
        method, args = self.parse_command(command)

        if not method:
            return

        if method in ("help", "?"):
            self.print_help()
            return

        if method == "history":
            for i, cmd in enumerate(self.history):
                print(f"{Colors.DIM}{i + 1:3d}. {cmd}{Colors.RESET}")
            return

        if method == "last":
            if self.last_response:
                print(json.dumps(self.last_response, indent=2, ensure_ascii=False))
            else:
                print(f"{Colors.DIM}No previous response{Colors.RESET}")
            return

        if method in ("clear", "cls"):
            print("\033[2J\033[H", end="")
            self.print_banner()
            return

        if method in ("exit", "quit", "q"):
            print(f"{Colors.BRIGHT_YELLOW}Goodbye!{Colors.RESET}")
            await self.client.aclose()
            raise SystemExit(0)

        method_map = {
            "g": "GET",
            "p": "POST",
            "pu": "PUT",
            "pa": "PATCH",
            "d": "DELETE",
        }

        if method in method_map:
            method = method_map[method]

        valid_methods = ["get", "post", "put", "patch", "delete", "head", "options"]
        if method.lower() not in valid_methods:
            print(f"{Colors.RED}Unknown command: {method}{Colors.RESET}")
            print(f"Type {Colors.CYAN}help{Colors.RESET} for available commands")
            return

        method = method.upper()

        kwargs = self.parse_args(args)

        if not kwargs["url"]:
            print(f"{Colors.RED}URL is required{Colors.RESET}")
            print(f"Usage: {method.lower()} <url> [options]")
            return

        method_color = self.get_method_color(method)
        url = self._check_https_url(kwargs["url"])
        print(f"{method_color}{method}{Colors.RESET} {Colors.GREEN}{url}{Colors.RESET}")

        if kwargs["headers"]:
            print(f"  {Colors.DIM}Headers: {kwargs['headers']}{Colors.RESET}")
        if kwargs["json"]:
            print(f"  {Colors.DIM}JSON: {json.dumps(kwargs['json'], ensure_ascii=False)[:100]}{Colors.RESET}")
        if kwargs.get("proxy"):
            print(f"  {Colors.DIM}Proxy: {kwargs['proxy']}{Colors.RESET}")

        url = self._check_https_url(kwargs.pop("url"))
        resp = await self.execute_request(method, url, **kwargs)

        if resp:
            try:
                self.last_response = resp.json()
            except Exception:
                self.last_response = {"text": resp.text}

            output = self.format_output(resp, kwargs["output"])
            print(output)

    async def run(self):
        """Run the REPL."""
        self.print_banner()

        while True:
            try:
                line = input(self.get_prompt()).strip()

                if not line:
                    continue

                self.history.append(line)

                await self.run_command(line)

            except KeyboardInterrupt:
                print(f"\n{Colors.BRIGHT_YELLOW}Use 'exit' or 'q' to quit{Colors.RESET}")
            except EOFError:
                print(f"\n{Colors.BRIGHT_YELLOW}Goodbye!{Colors.RESET}")
                break
            except SystemExit:
                break

        await self.client.aclose()


async def start_repl(proxy: str | None = None) -> None:
    """Start the interactive REPL."""
    repl = FastHTTPRepl(proxy=proxy)
    await repl.run()


def main(proxy: str | None = None) -> None:
    """Entry point for REPL."""
    asyncio.run(start_repl(proxy))


if __name__ == "__main__":
    main()
