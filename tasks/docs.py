"""Invoke MkDocs commands."""

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

CONFIG_FILE = "mkdocs.yml"


@task
def serve_docs(c: Context) -> None:
    """Serve the MkDocs documentation for live editing."""
    c.run("poetry install")  # This fixes module not found errors
    c.run(
        f"mkdocs serve \
        --config-file {CONFIG_FILE} \
        --watch src/ \
        --watch tasks/ ",
    )


@task
def build_docs(c: Context) -> None:
    """Build the MkDocs documentation with PDF export enabled."""
    import sys
    from pathlib import Path

    pdf_file = Path("site/pdf/combined.pdf")
    c.run("poetry install")  # This fixes module not found errors
    c.run(
        f"mkdocs build --clean --strict --config-file {CONFIG_FILE}",
        env={"ENABLE_PDF_EXPORT": "1"},
    )
    if not pdf_file.exists():
        print(f"Error: PDF file {pdf_file} was not created.")
        sys.exit(1)


@task
def ci_docs(c: Context) -> None:
    """Run all documentation checks."""
    build_docs(c)


doc_ns = Collection("docs")
doc_ns.add_task(serve_docs, name="serve")  # type: ignore[arg-type]
doc_ns.add_task(build_docs, name="build")  # type: ignore[arg-type]
doc_ns.add_task(ci_docs, name="ci")  # type: ignore[arg-type]
