"""Shared test setup: a temporary Knowledge Base, so tests never touch the real files."""

import json
import time

import pytest
from click.testing import CliRunner

import agent.cli as cli_module


SAMPLE_DATA = {
    "project": "Test Project",
    "last_updated": "2026-01-01",
    "test_cases": [
        {
            "id": "TC-001",
            "work_item_type": "Test Case",
            "title": "Login with valid credentials",
            "area_path": "App/Login",
            "assigned_to": "Diogo",
            "state": "Failed",
            "playwright_file": "tests/test_login.py",
            "steps": [{"step": 1, "action": "Open the login page", "expected": "Login page is shown"}],
        },
        {
            "id": "TC-002",
            "work_item_type": "Test Case",
            "title": "Reset password",
            "area_path": "App/Login",
            "assigned_to": "Ana",
            "state": "Active",
            "playwright_file": "",
            "steps": [{"step": 1, "action": "Click 'Forgot password'", "expected": "Reset form is shown"}],
        },
    ],
}


@pytest.fixture
def kb(tmp_path, monkeypatch):
    """Creates a temporary Knowledge Base and points the CLI to it."""
    (tmp_path / "test_cases.json").write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")
    (tmp_path / "history.json").write_text(json.dumps({"events": []}), encoding="utf-8")

    monkeypatch.setattr(cli_module, "TEST_CASES_PATH", str(tmp_path / "test_cases.json"))
    monkeypatch.setattr(cli_module, "HISTORY_PATH", str(tmp_path / "history.json"))
    monkeypatch.setattr(cli_module, "SUITES_PATH", str(tmp_path / "suites.json"))
    monkeypatch.setattr(cli_module, "CONFIG_PATH", str(tmp_path / "config.json"))
    monkeypatch.setattr(cli_module, "CACHE_PATH", str(tmp_path / ".ai_cache.json"))

    # The simulate mode waits half a second per step. Tests don't need to wait.
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    return tmp_path


@pytest.fixture
def runner():
    """Runs CLI commands inside the tests, as if they were typed in the terminal."""
    return CliRunner()