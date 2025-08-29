"""Python workflow tasks."""

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task


@task
def pip_upgrade(c: Context) -> None:
    """Upgrade pip dependencies."""
    c.run("poetry up")


@task
def ruff(c: Context) -> None:
    """Run the ruff linter."""
    print("\n👟 Running ruff\n")
    c.run("poetry run ruff check --fix", pty=True)


@task
def mypy_python(c: Context) -> None:
    """Run the mypy type checker."""
    print("\n👟 Running mypy\n")
    c.run("poetry run mypy ./src", pty=True)


@task
def test_static(c: Context) -> None:
    """Run all static checks for Python."""
    print("\n👟 Running static checks\n")
    ruff(c)
    mypy_python(c)


@task(pre=[ruff])
def test_unit(c: Context, report: bool = False) -> None:
    """Unit tests that run quickly.

    Args:
        c (Context): The context object.
        report (bool): Whether to generate a html coverage report.
    """
    print("\n👟 Running pytest\n")
    c.run("poetry install")  # fixes internal module not found
    cmd = "poetry run pytest tests/"
    if report:
        cmd += " --cov-report=html"
    c.run(cmd, pty=True)


@task
def test(c: Context) -> None:
    """Run all Python tests."""
    test_static(c)
    test_unit(c)


@task
def build(c: Context) -> None:
    """Build the project."""
    print("\n👟 Building project\n")
    c.run("poetry build --clean --format wheel")


@task
def ci_python(c: Context) -> None:
    """Run all Python checks during development."""
    pip_upgrade(c)
    test_static(c)
    test_unit(c)
    build(c)


python_ns = Collection("python")
python_ns.add_task(ruff, name="ruff")  # type: ignore[arg-type]
python_ns.add_task(mypy_python, name="mypy")  # type: ignore[arg-type]
python_ns.add_task(test, name="test")  # type: ignore[arg-type]
python_ns.add_task(test_static, name="test_static")  # type: ignore[arg-type]
python_ns.add_task(test_unit, name="test_unit")  # type: ignore[arg-type]
python_ns.add_task(pip_upgrade, name="pip_upgrade")  # type: ignore[arg-type]
python_ns.add_task(build, name="build")  # type: ignore[arg-type]
python_ns.add_task(ci_python, name="ci")  # type: ignore[arg-type]
