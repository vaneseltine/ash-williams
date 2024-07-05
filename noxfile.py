#! /usr/bin/env python3
# type: ignore
"""
Invoke via `nox` or `python -m nox`

nox -k "lint"   lint only
nox -k "test"   pytest plus coverage
nox             everything

See: https://nox.thea.codes/en/stable/cookbook.html
"""

import os
import re
import sys
from pathlib import Path

import nox

nox.options.stop_on_first_error = False
nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = "yes"

PACKAGE_NAME = "ash"

IN_CI = os.getenv("CI", "").lower() == "true"
IN_WINDOWS = sys.platform.startswith("win")


def supported_pythons(classifiers_file=Path("setup.cfg")):
    """
    Parse all supported Python classifiers from setup.cfg
    """
    if IN_WINDOWS:
        return None
    pattern = re.compile(r"Programming Language :: Python :: ([0-9]+\.[0-9.]+)")
    return pattern.findall(classifiers_file.read_text())


@nox.session(python=False)
def lint_black(session):
    session.run("python", "-m", "black", ".")


@nox.session(python=False)
def lint_pylint(session):
    cmd = f"python -m pylint {PACKAGE_NAME} --score=no"
    session.run(*cmd.split())


@nox.session(python=False)
def lint_pyright(session, subfolder=PACKAGE_NAME):
    session.run(
        "python",
        "-m",
        "pyright",
        subfolder,
        env={"PYRIGHT_PYTHON_FORCE_VERSION": "latest"},  # hush
    )


# @nox.session(python=supported_pythons(), reuse_venv=False)
@nox.session(python=False)
def test_pytest(session):
    """
    pytest-xdist can be installed to allow threaded parallel testing. But it is most
    likely that many tests will be required to compensate for the added overhead
    spinning up workers.
    """
    # session.install("-r", "requirements-dev.txt")
    # session.install("-e", ".")
    cmd = ["python", "-m", "coverage", "run", "-m", "pytest"]
    session.run(*cmd)
    session.run("python", "-m", "coverage", "report")


@nox.session(python=False)
def test_coverage(session):
    # session.run("coveralls", success_codes=[0, 1]) # requires public GitHub
    session.run("python", "-m", "coverage", "html")


@nox.session(python=False)
def lint_todos(_):
    for file in Path(".").glob("*/*.py"):
        result = search_in_file(file, "((TODO|FIXME).*)")
        for line in result:
            print(f"{file.name:>20}: {line}")


def search_in_file(path, pattern, encoding="utf-8"):
    text = Path(path).read_text(encoding)
    results = re.compile(pattern).findall(text)
    return [line for line, _match in results]


# @nox.session(python=False)
# def autopush_repo(session):
#     if not nox.options.stop_on_first_error:
#         session.skip("Error-free runs required")
#     git_output = subprocess.check_output(["git", "status", "--porcelain"])
#     if git_output:
#         print(git_output.decode("ascii").rstrip())
#         session.skip("Local repo is not clean")
#     # if not AT_HOME:
#     #     session.skip("Only from home")
#     subprocess.check_output(["git", "push"])


if __name__ == "__main__":
    print(f"Invoke {__file__} by running Nox.")
    import subprocess

    subprocess.run(["nox"])
