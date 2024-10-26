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

nox.options.python = "3.12"
nox.options.default_venv_backend = "uv"


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
def formatting(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), "ruff")
    session.run("ruff", "format")


@nox.session(python=["3.12"], tags=["typing"])
def typing(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), ".[typing]")
    session.run("mypy")


@nox.session(python=["3.12"], tags=["test"])
def test(session: Session) -> None:
    """
    Run pytest if test target files exist in src directory.
    Skip otherwise.
    """
    if not has_test_targets():
        session.skip("No test targets found in src directory")

    session.install("-c", constraints(session).as_posix(), ".[tests]")
    session.run("pytest")


@nox.session(python=["3.12"], venv_backend="uv", tags=["security"])
def security(session: Session) -> None:
    session.install("-c", constraints(session).as_posix(), ".[dev]")
    session.run("bandit", "-r", "src")
