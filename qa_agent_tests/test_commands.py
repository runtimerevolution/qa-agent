"""Tests for CLI commands, using the temporary Knowledge Base from conftest.py."""

import json

from agent.cli import cli


def read_states(kb):
    """Returns the state of each test case, read from the temporary Knowledge Base."""
    data = json.loads((kb / "test_cases.json").read_text(encoding="utf-8"))
    return {tc["id"]: tc["state"] for tc in data["test_cases"]}


# --- update-state ---

def test_update_state_changes_the_state(kb, runner):
    result = runner.invoke(cli, ["update-state", "TC-002", "Passed"])

    assert result.exit_code == 0
    assert read_states(kb)["TC-002"] == "Passed"


def test_update_state_rejects_invalid_states(kb, runner):
    result = runner.invoke(cli, ["update-state", "TC-002", "Done"])

    assert "Invalid state" in result.output
    assert read_states(kb)["TC-002"] == "Active"


# --- list-tests ---

def test_list_tests_json_returns_valid_json(kb, runner):
    result = runner.invoke(cli, ["list-tests", "--json"])
    data = json.loads(result.output)

    assert data[0]["id"] == "TC-001"
    assert data[0]["has_playwright"] is True
    assert data[1]["has_playwright"] is False


# --- run-tests ---

def test_run_tests_runs_failed_tests_and_updates_their_state(kb, runner):
    result = runner.invoke(cli, ["run-tests", "--state", "Failed", "--simulate"], input="y\n")

    assert result.exit_code == 0
    assert "TC-001" in result.output
    assert read_states(kb)["TC-001"] == "Passed"


def test_run_tests_skips_tests_without_playwright(kb, runner):
    result = runner.invoke(
        cli, ["run-tests", "--id", "TC-001", "--id", "TC-002", "--simulate"], input="y\n"
    )

    assert "Skipped" in result.output
    assert read_states(kb)["TC-002"] == "Active"


def test_run_tests_cancelled_changes_nothing(kb, runner):
    result = runner.invoke(cli, ["run-tests", "--state", "Failed", "--simulate"], input="n\n")

    assert "cancelled" in result.output
    assert read_states(kb)["TC-001"] == "Failed"


def test_run_tests_without_filters_defaults_to_no(kb, runner):
    result = runner.invoke(cli, ["run-tests", "--simulate"], input="\n")

    assert "cancelled" in result.output
    assert read_states(kb)["TC-001"] == "Failed"


# --- suites ---

def test_suite_save_normalises_name_and_ids(kb, runner):
    result = runner.invoke(cli, ["suite-save", "My Suite", "--id", "tc-001"])
    suites = json.loads((kb / "suites.json").read_text(encoding="utf-8"))["suites"]

    assert result.exit_code == 0
    assert suites["my-suite"]["test_ids"] == ["TC-001"]


def test_suite_save_rejects_unknown_ids(kb, runner):
    result = runner.invoke(cli, ["suite-save", "bad", "--id", "TC-999"])

    assert "not found" in result.output
    assert not (kb / "suites.json").exists()


def test_run_suite_runs_the_suite_tests(kb, runner):
    runner.invoke(cli, ["suite-save", "smoke", "--id", "TC-001"])
    result = runner.invoke(cli, ["run-suite", "smoke", "--simulate"], input="y\n")

    assert "Suite: smoke" in result.output
    assert read_states(kb)["TC-001"] == "Passed"


# --- AI ---

def test_generate_test_stops_before_questions_when_ai_is_off(kb, runner):
    (kb / "config.json").write_text(json.dumps({"ai_enabled": False}), encoding="utf-8")

    result = runner.invoke(cli, ["generate-test"])

    assert "AI features are turned off" in result.output
    assert "Describe the feature" not in result.output
    