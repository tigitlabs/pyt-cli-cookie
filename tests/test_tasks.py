"""Tests for the invoke tasks."""

import subprocess


def test_invoke_list():
    """Smoke test for 'invoke -l' to ensure it lists tasks without errors."""
    # Run invoke -l and capture output
    result = subprocess.run(
        ["invoke", "-l"],
        capture_output=True,
        text=True,
        cwd=".",
    )
    assert result.returncode == 0, f"'invoke -l' failed with exit code {result.returncode}: {result.stderr}"
    expected_tasks = ["python.ci"]
    output = result.stdout
    for task in expected_tasks:
        assert task in output, f"Task '{task}' not found in 'invoke -l' output: {output}"
