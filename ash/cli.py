from pprint import pformat

import click

from ash.main import Paper, RetractionDatabase


@click.command(no_args_is_help=True)
@click.argument("paper", required=True)
@click.option("--database", help="Path to retractions database file.")
def ash_cli(paper: str, database: str):
    """
    Simple program that runs Ash on PAPER using DATABASE.
    """
    print_basic_report(paper, database)


def print_basic_report(paper_spec: str, database_spec: str):
    db = RetractionDatabase(database_spec)
    paper = Paper.from_path(paper_spec)
    prettied = pformat(paper.report(db, validate_dois=False))
    click.echo(prettied)
