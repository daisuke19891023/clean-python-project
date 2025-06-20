#!/usr/bin/env python3
import pathlib
import platform
import sys
from pathlib import Path

import nox
from nox.sessions import Session

# nox usage example
# @nox.session(python=["3.12"], venv_backend="uv", tags=["example"])
# def example(session: Session) -> None:
#     session.install("-c", constraints(session).as_posix(), ".[AAA]")  # noqa: ERA001
#     session.run("EXAMPLE_COMMAND")    # noqa: ERA001

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True

# Coverage threshold
COVER_MIN = 80

def has_test_targets() -> bool:
    """
    Check if there are any Python files in the src directory to test.

    Returns:
        bool: True if test target files exist, False otherwise
    """
    src_path = pathlib.Path("src")
    if not src_path.exists():
        return False

    # Return True if any .py files exist in src directory (recursive search)
    return any(src_path.glob("**/*.py"))


def constraints(session: Session) -> Path:
    # Automatically create constraints file name
    filename = f"python{session.python}-{sys.platform}-{platform.machine()}.txt"
    return Path("constraints", filename)


@nox.session(python=["3.12"], venv_backend="uv")
def lock(session: Session) -> None:
    filename = constraints(session)
    filename.parent.mkdir(exist_ok=True)
    session.run(
        "uv",
        "pip",
        "compile",
        "pyproject.toml",
        "--upgrade",
        "--quiet",
        "--all-extras",
        f"--output-file={filename}",
    )


@nox.session(python=["3.12"], tags=["lint"])
def lint(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), "ruff")
    session.run("ruff", "check")


@nox.session(python=["3.12"], tags=["format"])
def format_code(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), "ruff")
    session.run("ruff", "format")


@nox.session(python=["3.12"], tags=["sort"])
def sort(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), "ruff")
    session.run("ruff", "check", "--select", "I", "--fix")


@nox.session(python=["3.12"], tags=["typing"])
def typing(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), ".[dev]")
    session.run("pyright")


@nox.session(python=["3.12"], tags=["pyright"])
def pyright(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), "pyright")
    session.run("pyright")


@nox.session(python=["3.12"], tags=["test"])
def test(session: Session) -> None:
    """
    Run pytest if test target files exist in src directory.
    Skip otherwise.
    """
    if not has_test_targets():
        session.skip("No test targets found in src directory")

    session.install("-c", constraints(session).as_posix(), ".[tests]")
    session.run("pytest", "--cov=src", f"--cov-fail-under={COVER_MIN}")


@nox.session(python=["3.12"], tags=["security"])
def security(session: Session) -> None:
    """Run security checks: bandit, pip-audit, safety"""
    session.install("-c", constraints(session).as_posix(), ".[dev]")
    session.run("bandit", "-r", "src")
    session.run("pip-audit")
    session.run("safety", "check", "--full-report")


@nox.session(python=["3.12"], tags=["docs"])
def docs(session: Session) -> None:
    """Build documentation with MkDocs"""
    session.install("-c", constraints(session).as_posix(), ".[docs]")
    session.run("mkdocs", "build", "--strict")


@nox.session(python=["3.12"], tags=["ci"])
def ci(session: Session) -> None:
    """Run all CI checks: lint, format, typing, test, security"""
    session.notify("lint")
    session.notify("format_code")
    session.notify("typing")
    session.notify("test")
    session.notify("security")


@nox.session(python=["3.12"], tags=["all"])
def all_checks(session: Session) -> None:
    """Run all quality checks: lint, format_code, sort, typing, pyright, test, security, docs"""
    session.notify("lint")
    session.notify("format_code")
    session.notify("sort")
    session.notify("typing")
    session.notify("pyright")
    session.notify("test")
    session.notify("security")
    session.notify("docs")
