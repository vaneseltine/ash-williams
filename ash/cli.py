from pathlib import Path
from pprint import pformat

import click

from ash import config
from ash.main import Paper, RetractionDatabase

stored_database = config.read_value(table="database", key="path")


@click.command(no_args_is_help=True)
@click.argument("paper", type=click.Path(exists=True), required=False)
@click.option(
    "--database",
    help="Path to retractions database file.",
    default=stored_database,
    show_default=True,
    type=click.Path(),
)
@click.option(
    "--clear", help="Clear saved retractions database file path.", is_flag=True
)
@click.pass_context
def ash_cli(ctx: click.Context, paper: str, database: str | Path | None, clear: bool):
    """
    Simple program that runs Ash on PAPER using DATABASE.
    """
    if clear:
        _ = config.write_value(
            table="database", key="path", value=""
        )  # pylint: disable=assignment-from-none
        click.echo("Removing previously recorded path of saved retractions database.")
        ctx.exit()
    database = locate_database(database)
    if database is None:
        click.echo(
            "Error: You must specify the path of a retractions database with --database."
        )
        ctx.exit()
    click.echo(f"Using database at {database}...")
    print_basic_report(paper, database)


def locate_database(database: str | Path | None) -> Path | None:
    database = database or stored_database
    if database is None or database == "":
        return None
    _ = config.write_value(table="database", key="path", value=database)
    return Path(database)


def print_basic_report(paper_spec: str, database_spec: str | Path):
    db = RetractionDatabase(database_spec)
    paper = Paper.from_path(paper_spec)
    prettied = pformat(paper.report(db, validate_dois=False))
    click.echo(prettied)
