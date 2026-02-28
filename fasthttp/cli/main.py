import typer

from fasthttp.cli.commands import app as commands_app
from fasthttp.cli.output import formatter

app = typer.Typer(
    name="fasthttp",
    help="FastHTTP CLI - Fast and simple HTTP client",
    add_completion=False,
)


@app.command()
def version() -> None:
    formatter.result("FastHTTP CLI", "v0.1.6")


app.add_typer(commands_app, name="")

__all__ = ("app",)
