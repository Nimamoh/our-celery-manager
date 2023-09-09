import typer

from .db import db_cli

cli = typer.Typer()

cli.add_typer(db_cli, name="db")

if __name__ == "__main__":
    cli()