# pylint: disable=unused-argument

import pytest
from click.testing import CliRunner

from ash import ash_cli


@pytest.mark.parametrize("args", [[], ["--help"]])
def test_help_works(args):
    runner = CliRunner()
    result = runner.invoke(ash_cli, args)
    assert result.exit_code == 0
    assert result.output.startswith("Usage")
    assert "help" in result.output
