import json
from typing import Any

import httpx
import typer

from fasthttp.cli.client import CLIResponse, run_request
from fasthttp.cli.output import formatter

app = typer.Typer(help="FastHTTP CLI - HTTP client from command line")


def parse_headers(headers_str: str | None) -> dict[str, str] | None:
    if not headers_str:
        return None

    headers = {}
    for item in headers_str.split(","):
        if ":" in item:
            key, value = item.split(":", 1)
            headers[key.strip()] = value.strip()
    return headers


def get_output(resp: CLIResponse, output: str) -> str:
    match output.lower():
        case "status":
            return str(resp.status)
        case "headers":
            import json

            return json.dumps(resp.headers, indent=2)
        case "json":
            if resp.json_data:
                import json

                return json.dumps(resp.json_data, indent=2)
            return "(no JSON in response)"
        case "text":
            return resp.text
        case "all":
            import json

            return (
                f"Status: {resp.status}\n"
                f"Elapsed: {resp.elapsed_ms:.2f}ms\n"
                f"Headers:\n{json.dumps(resp.headers, indent=2)}\n"
                f"Body:\n{resp.text[:500]}"
            )
        case _:
            return f"Unknown output type: {output}"


@app.command()
def get(
    url: str,
    output: str = typer.Argument("status", help="Output: status, headers, json, text, all"),
    headers: str | None = typer.Option(None, "-H", "--header", help="Headers (Key:Value,Key2:Value2)"),
    timeout: float = typer.Option(30.0, "-t", "--timeout", help="Request timeout in seconds"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
) -> None:
    _execute_request("GET", url, output, headers, timeout=timeout, debug=debug)


@app.command()
def post(
    url: str,
    output: str = typer.Argument("status", help="Output: status, headers, json, text, all"),
    headers: str | None = typer.Option(None, "-H", "--header", help="Headers (Key:Value,Key2:Value2)"),
    json_body: str | None = typer.Option(None, "-j", "--json", help="JSON body"),
    data: str | None = typer.Option(None, "-d", "--data", help="Form data"),
    timeout: float = typer.Option(30.0, "-t", "--timeout", help="Request timeout in seconds"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
) -> None:
    json_data: dict[str, Any] | None = None
    if json_body:
        try:
            json_data = json.loads(json_body)
        except json.JSONDecodeError as e:
            formatter.error(f"Invalid JSON: {e}")
            raise typer.Exit(1)

    _execute_request("POST", url, output, headers, json_data=json_data, data=data, timeout=timeout, debug=debug)


@app.command()
def put(
    url: str,
    output: str = typer.Argument("status", help="Output: status, headers, json, text, all"),
    headers: str | None = typer.Option(None, "-H", "--header", help="Headers (Key:Value,Key2:Value2)"),
    json_body: str | None = typer.Option(None, "-j", "--json", help="JSON body"),
    data: str | None = typer.Option(None, "-d", "--data", help="Form data"),
    timeout: float = typer.Option(30.0, "-t", "--timeout", help="Request timeout in seconds"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
) -> None:
    json_data: dict[str, Any] | None = None
    if json_body:
        try:
            json_data = json.loads(json_body)
        except json.JSONDecodeError as e:
            formatter.error(f"Invalid JSON: {e}")
            raise typer.Exit(1)

    _execute_request("PUT", url, output, headers, json_data=json_data, data=data, timeout=timeout, debug=debug)


@app.command()
def patch(
    url: str,
    output: str = typer.Argument("status", help="Output: status, headers, json, text, all"),
    headers: str | None = typer.Option(None, "-H", "--header", help="Headers (Key:Value,Key2:Value2)"),
    json_body: str | None = typer.Option(None, "-j", "--json", help="JSON body"),
    data: str | None = typer.Option(None, "-d", "--data", help="Form data"),
    timeout: float = typer.Option(30.0, "-t", "--timeout", help="Request timeout in seconds"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
) -> None:
    json_data: dict[str, Any] | None = None
    if json_body:
        try:
            json_data = json.loads(json_body)
        except json.JSONDecodeError as e:
            formatter.error(f"Invalid JSON: {e}")
            raise typer.Exit(1)

    _execute_request("PATCH", url, output, headers, json_data=json_data, data=data, timeout=timeout, debug=debug)


@app.command()
def delete(
    url: str,
    output: str = typer.Argument("status", help="Output: status, headers, json, text, all"),
    headers: str | None = typer.Option(None, "-H", "--header", help="Headers (Key:Value,Key2:Value2)"),
    timeout: float = typer.Option(30.0, "-t", "--timeout", help="Request timeout in seconds"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
) -> None:
    _execute_request("DELETE", url, output, headers, timeout=timeout, debug=debug)


def _execute_request(
    method: str,
    url: str,
    output: str,
    headers_str: str | None,
    json_data: dict | None = None,
    data: str | None = None,
    timeout: float = 30.0,
    debug: bool = False,
) -> None:
    headers = parse_headers(headers_str)

    if debug:
        formatter.info(f"→ {method} {url}")
        if headers:
            formatter.info(f"  Headers: {json.dumps(headers, indent=2)}")
        if json_data:
            formatter.info(f"  JSON: {json.dumps(json_data, indent=2)}")
        if data:
            formatter.info(f"  Data: {data}")

    try:
        resp = run_request(
            method=method,
            url=url,
            headers=headers,
            json_data=json_data,
            data=data,
            timeout=timeout,
        )

        if resp.status >= 400:
            formatter.error(f"HTTP {resp.status}")
            formatter.result("body", resp.text[:200])
            raise typer.Exit(1)

        formatter.success(f"HTTP {resp.status} in {resp.elapsed_ms:.2f}ms")

        if debug:
            formatter.info(f"← Response headers:")
            for key, value in resp.headers.items():
                formatter.info(f"  {key}: {value}")

        result = get_output(resp, output)
        print(result)

    except httpx.ConnectError as e:
        formatter.error(f"Connection failed: {e}")
        raise typer.Exit(1)
    except httpx.TimeoutException as e:
        formatter.error(f"Request timed out: {e}")
        raise typer.Exit(1)
    except Exception as e:
        formatter.error(f"Error: {e}")
        raise typer.Exit(1)
