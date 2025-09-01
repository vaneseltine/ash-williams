# pylint: disable=unused-argument

import pytest
from click.testing import CliRunner

from ash import ash_cli


@pytest.mark.parametrize(
    "args, exit_code",
    [
        ([], 2),
        (["--help"], 0),
    ],
)
def test_help_works(args, exit_code):
    runner = CliRunner()
    result = runner.invoke(ash_cli, args)
    assert result.exit_code == exit_code
    assert result.output.startswith("Usage")
    assert "help" in result.output
