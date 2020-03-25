from datetime import datetime
from . import __version__
from .core import run
import typer

app = typer.Typer()

def version_callback(value: bool):
    if value:
        typer.echo(f"Awesome USD Quotes Version: {__version__}")
        raise typer.Exit()

@app.command()
def main(
    data: datetime = typer.Argument(..., formats=["%Y%m%d",]),
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version info",
    ),
):
    """
    USD Quotes, Get lowest currency against USD

    Provide a Date in format YYYYMMDD as argument to CLI

    Example: python -m usdquote.main 20191131
    
    """

    run(data)


if __name__ == "__main__":
    app()
