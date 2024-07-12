"""
See: https://nox.thea.codes/en/stable/cookbook.html
"""

import os
import re
from pathlib import Path
from typing import Any

import nox
from nox.sessions import Session

CODE_DIR = "ash"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
IN_CI = os.getenv("CI", "").lower() == "true"


nox.options.default_venv_backend = "venv"
# nox.options.reuse_existing_virtualenvs = "no"
nox.options.error_on_external_run = "yes"

# Default run
nox.options.sessions = [
    "lint_black",
    "lint_pylint",
    "lint_pyright",
    "test_pytest_single",
    "lint_todos",
]


def run(session: Session, cmd: str, **kwargs: dict[str, Any]):
    _ = session.run(*cmd.split(), **kwargs)  # pyright: ignore[reportArgumentType]


def install(session: Session, cmd: str, **kwargs: dict[str, Any]):
    _ = session.install(*cmd.split(), **kwargs)  # pyright: ignore[reportArgumentType]


def supported_pythons(classifiers_file: str | Path = "pyproject.toml"):
    """
    Parse all supported Python classifiers.

    E.g., pyproject.toml including:

        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        # "Programming Language :: Python :: 3.13", # I did comment this and yet
        "Programming Language :: Python :: 3 :: Only",

    Becomes:

        ['3.12', '3.13']

    Note that comments are included in this search.
    """
    pattern = re.compile(r"Programming Language :: Python :: ([0-9]+\.[0-9.]+)")
    pythons = pattern.findall(Path(classifiers_file).read_text(encoding="utf-8"))
    return sorted(pythons)


@nox.session(python=False)
def lint_black(session: Session):
    files = [path for path in Path(__file__).parent.glob("*/*.py")]
    _ = session.run("python", "-m", "black", *files)


@nox.session(python=False)
def lint_pylint(session: Session):
    run(session, f"python -m pylint {CODE_DIR} --score=no")


@nox.session(python=False)
def lint_pyright(session: Session):
    run(
        session,
        f"python -m pyright {CODE_DIR}",
        env={"PYRIGHT_PYTHON_FORCE_VERSION": "latest"},  # hush
    )


@nox.session(python=False)
def test_pytest_single(session: Session):
    """
    Simple, non-environment run with coverage.

    pytest-xdist can be installed to allow threaded parallel testing with "-n auto."
    But it takes a couple seconds just to spin up the workers, so unless testing is
    taking long enough to compensate, it's overkill.
    """
    run(session, "python -m pytest --cov=ash --durations=5")
    run(session, "python -m coverage html")


@nox.session(python=supported_pythons(), reuse_venv=False)
def test_pytest_multipython(session: Session):
    install(session, "-r requirements-dev.txt")
    install(session, "-e .")
    run(
        session,
        "python -m pytest",
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )


@nox.session(python=False)
def lint_todos(_):
    for file in Path(".").glob("*/*.py"):
        result = search_in_file(file, "((TODO|FIXME|XXX).*)")
        for line in result:
            print(f"{file.name:>20}: {line}")


@nox.session
def check_build(session: Session):
    install(session, "-r requirements.txt")
    install(session, "build twine")
    run(session, "python -m build")
    run(session, "python -m twine check dist/*")


def search_in_file(path: Path, pattern: str, encoding: str = "utf-8"):
    text = Path(path).read_text(encoding)
    results = re.compile(pattern).findall(text)
    return [line for line, _match in results]
