import typer

from fasthttp.__meta__ import __version__
from fasthttp.cli.commands import app as commands_app
from fasthttp.cli.output import formatter
from fasthttp.cli.run import run_app

app = typer.Typer(
    name="fasthttp",
    help="FastHTTP CLI - Fast and simple HTTP client",
    add_completion=False,
    invoke_without_command=True,
)


@app.command()
def version() -> None:
    formatter.result("FastHTTP CLI", f"v{__version__}")


@app.command()
def repl(
    proxy: str | None = typer.Option(
        None, "-p", "--proxy",
        help="Proxy URL (http://, https://, socks5://)"
    ),
) -> None:
    """Start interactive REPL mode."""
    from fasthttp.cli.repl import main
    main(proxy=proxy)


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    """Default command - start REPL."""
    if ctx.invoked_subcommand is None:
        from fasthttp.cli.repl import main
        main()


app.add_typer(commands_app, name="")
app.add_typer(run_app, name="")

__all__ = ("app",)
