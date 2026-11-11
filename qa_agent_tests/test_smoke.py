"""Smoke tests: check that the QA Agent and all its commands start, the same way the menu calls them."""

import subprocess
import sys

import pytest

import agent.menu as menu
from agent.cli import cli


EXPECTED_COMMANDS = {
    "list-tests", "show", "add-test", "update-test", "update-state", "assign",
    "delete-test", "search", "stats", "run-test", "run-tests", "suites",
    "run-suite", "suite-save", "suite-delete", "roadmap", "history",
    "ask", "generate-test", "clear-cache", "doctor",
}


def run_cli(*args):
    """Runs the CLI as a separate program, exactly like the menu does."""
    return subprocess.run(
        [sys.executable, "-m", "agent.cli", *args],
        capture_output=True,
        text=True,
        cwd=menu.BASE_DIR,
    )


def test_cli_starts():
    result = run_cli("--help")
    assert result.returncode == 0, result.stderr


def test_all_expected_commands_exist():
    missing = EXPECTED_COMMANDS - set(cli.commands)
    assert not missing, f"Missing commands: {missing}"


@pytest.mark.parametrize("command", sorted(cli.commands))
def test_every_command_shows_its_help(command):
    result = run_cli(command, "--help")
    assert result.returncode == 0, result.stderr


def test_menu_can_read_data_from_the_cli():
    test_cases = menu.get_command_json(["list-tests", "--json"])
    assert isinstance(test_cases, list)