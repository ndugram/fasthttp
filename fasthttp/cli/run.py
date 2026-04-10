from pathlib import Path
from typing import Any

import typer

from fasthttp.cli.output import formatter

run_app = typer.Typer(help="Run FastHTTP application from file")


def _load_app_from_file(file_path: Path) -> Any:
    """
    Load FastHTTP app instance from Python file.

    Args:
        file_path: Path to the Python file containing the app.

    Returns:
        FastHTTP app instance.

    Raises:
        typer.Exit: If app cannot be loaded.
    """
    import sys
    from importlib.util import module_from_spec, spec_from_file_location

    if not file_path.exists():
        formatter.error(f"File not found: {file_path}")
        raise typer.Exit(1)

    if file_path.suffix != ".py":
        formatter.error(f"Expected Python file, got: {file_path.suffix}")
        raise typer.Exit(1)

    module_name = file_path.stem
    spec = spec_from_file_location(module_name, file_path)

    if spec is None or spec.loader is None:
        formatter.error(f"Cannot load module from: {file_path}")
        raise typer.Exit(1)

    module = module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        formatter.error(f"Failed to execute {file_path.name}: {e}")
        raise typer.Exit(1)

    app = None
    for name in dir(module):
        obj = getattr(module, name)
        from fasthttp import FastHTTP

        if isinstance(obj, FastHTTP):
            app = obj
            break

    if app is None:
        formatter.error(
            f"No FastHTTP app found in {file_path.name}. "
            "Make sure you have 'app = FastHTTP(...)' in your file."
        )
        raise typer.Exit(1)

    return app


@run_app.command(name="run")
def run_command(
    file: Path = typer.Argument(
        ...,
        help="Path to Python file with FastHTTP app",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    tags: str | None = typer.Option(
        None,
        "-t",
        "--tags",
        help="Run only routes with specific tags (comma-separated)",
    ),
    debug: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Enable debug mode",
    ),
) -> None:
    """
    Run FastHTTP app in request mode.

    Executes all registered HTTP requests and displays results.
    """
    formatter.info(f"Loading app from: {file}")

    app = _load_app_from_file(file)

    if debug:
        app.logger.setLevel("DEBUG")
        app.debug = True

    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",")]
        formatter.info(f"Running with tags: {tags_list}")

    print()
    formatter.header("FastHTTP Runner")
    formatter.key_value("Mode", "RUN")
    formatter.key_value("File", file.name)
    formatter.key_value("Routes", len(app.routes))
    if tags_list:
        formatter.key_value("Filtered tags", ", ".join(tags_list))
    print()

    app.run(tags=tags_list)


@run_app.command(name="dev")
def dev_command(
    file: Path = typer.Argument(
        ...,
        help="Path to Python file with FastHTTP app",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "-h",
        "--host",
        help="Host to bind the server to",
    ),
    port: int = typer.Option(
        8000,
        "-p",
        "--port",
        help="Port to bind the server to",
    ),
    base_url: str | None = typer.Option(
        None,
        "-b",
        "--base-url",
        help="Base URL prefix for documentation endpoints",
    ),
    debug: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Enable debug mode",
    ),
) -> None:
    """
    Run FastHTTP app in development mode with Swagger UI.

    Starts an ASGI server with interactive documentation.
    """
    formatter.info(f"Loading app from: {file}")

    app = _load_app_from_file(file)

    if debug:
        app.logger.setLevel("DEBUG")
        app.debug = True

    print()
    formatter.header("FastHTTP Dev Server")
    formatter.key_value("Mode", "DEV (Web UI)")
    formatter.key_value("File", file.name)
    formatter.key_value("Routes", len(app.routes))
    print()

    server_url = f"http://{host}:{port}"
    docs_url = f"{server_url}{base_url or ''}/docs"

    print(f"\n\033[92m\033[1m▲ FastHTTP\033[0m \033[90mdev server\033[0m")
    print(f"\033[94m➜\033[0m  Server:   \033[1m{server_url}\033[0m")
    print(f"\033[94m➜\033[0m  Docs:     \033[1m{docs_url}\033[0m")
    print(f"\033[90m─────────────────────────────────\033[0m\n")

    app.web_run(host=host, port=port, base_url=base_url)
