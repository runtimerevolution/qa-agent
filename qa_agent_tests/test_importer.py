"""Tests for reading test cases from CSV files."""

from agent.importer import DEFAULT_COLUMNS, parse_csv


HEADER = "ID,Title,Test Step,Step Action,Step Expected,Area Path,Assigned To,State\n"


def write_csv(tmp_path, content, encoding="utf-8"):
    """Writes a CSV file in the temporary folder and returns its path."""
    path = tmp_path / "import.csv"
    path.write_text(content, encoding=encoding)
    return path


def test_reads_test_cases_with_several_steps(tmp_path):
    path = write_csv(tmp_path, HEADER +
        "TC-101,Login,1,Open the login page,Login page is shown,App/Login,Diogo,Active\n"
        ",,2,Enter valid credentials,User is logged in,,,\n"
        "TC-102,Logout,1,Click logout,User is logged out,App/Login,Ana,Passed\n"
    )

    test_cases, problems = parse_csv(path, DEFAULT_COLUMNS)

    assert problems == []
    assert [tc["id"] for tc in test_cases] == ["TC-101", "TC-102"]
    assert [step["action"] for step in test_cases[0]["steps"]] == [
        "Open the login page", "Enter valid credentials"
    ]
    assert test_cases[0]["steps"][1]["step"] == 2
    assert test_cases[1]["assigned_to"] == "Ana"


def test_reads_files_separated_with_semicolons(tmp_path):
    path = write_csv(tmp_path,
        "ID;Title;Test Step;Step Action;Step Expected;Area Path;Assigned To;State\n"
        "TC-101;Login;1;Open the login page;Login page is shown;App/Login;Diogo;Active\n"
    )

    test_cases, problems = parse_csv(path, DEFAULT_COLUMNS)

    assert problems == []
    assert test_cases[0]["title"] == "Login"


def test_ignores_the_excel_bom(tmp_path):
    path = write_csv(tmp_path, HEADER +
        "TC-101,Login,1,Open the login page,Login page is shown,App/Login,Diogo,Active\n",
        encoding="utf-8-sig",
    )

    test_cases, problems = parse_csv(path, DEFAULT_COLUMNS)

    assert test_cases[0]["id"] == "TC-101"


def test_empty_state_becomes_active(tmp_path):
    path = write_csv(tmp_path, HEADER +
        "TC-101,Login,1,Open the login page,Login page is shown,App/Login,Diogo,\n"
    )

    test_cases, _ = parse_csv(path, DEFAULT_COLUMNS)

    assert test_cases[0]["state"] == "Active"


def test_ignores_empty_lines(tmp_path):
    path = write_csv(tmp_path, HEADER +
        "TC-101,Login,1,Open the login page,Login page is shown,App/Login,Diogo,Active\n"
        ",,,,,,,\n"
    )

    test_cases, problems = parse_csv(path, DEFAULT_COLUMNS)

    assert problems == []
    assert len(test_cases[0]["steps"]) == 1


def test_reports_missing_required_columns(tmp_path):
    path = write_csv(tmp_path, "ID,Title,Area Path\nTC-101,Login,App/Login\n")

    test_cases, problems = parse_csv(path, DEFAULT_COLUMNS)

    assert test_cases == []
    assert "Missing columns: Step Action" in problems[0]


def test_reports_steps_without_a_test_case(tmp_path):
    path = write_csv(tmp_path, HEADER +
        ",,1,Orphan step,Nothing,,,\n"
        "TC-101,Login,1,Open the login page,Login page is shown,App/Login,Diogo,Active\n"
    )

    test_cases, problems = parse_csv(path, DEFAULT_COLUMNS)

    assert "Line 2" in problems[0]
    assert len(test_cases) == 1


def test_custom_column_names(tmp_path):
    columns = {**DEFAULT_COLUMNS, "title": "Nome", "step_action": "Ação"}
    path = write_csv(tmp_path, "Nome,Ação\nLogin,Abrir a página\n")

    test_cases, problems = parse_csv(path, columns)

    assert problems == []
    assert test_cases[0]["title"] == "Login"
    assert test_cases[0]["steps"][0]["action"] == "Abrir a página"

    from agent.importer import next_test_id, plan_import

VALID_STATES = ["Active", "Passed", "Failed", "Blocked", "In Progress"]


def make_parsed(test_id="", title="New test", state="Active", steps=1, line=2):
    """Creates a test case as returned by parse_csv, for the tests below."""
    return {
        "id": test_id, "title": title, "area_path": "App", "assigned_to": "Diogo",
        "state": state, "line": line,
        "steps": [{"step": n, "action": f"Action {n}", "expected": ""} for n in range(1, steps + 1)],
    }


def test_next_test_id_follows_the_highest_number():
    assert next_test_id(["TC-001", "TC-007", "ABC", "TC-XYZ"]) == "TC-008"


def test_next_test_id_starts_at_one():
    assert next_test_id([]) == "TC-001"


def test_plan_import_skips_existing_ids_ignoring_case():
    existing = [{"id": "TC-001"}]
    to_add, skipped, _ = plan_import([make_parsed("tc-001")], existing, VALID_STATES)

    assert to_add == []
    assert "already exists" in skipped[0]


def test_plan_import_gives_ids_after_reading_the_whole_file():
    parsed = [make_parsed(""), make_parsed("TC-002")]
    to_add, _, _ = plan_import(parsed, [{"id": "TC-001"}], VALID_STATES)

    assert [tc["id"] for tc in to_add] == ["TC-003", "TC-002"]


def test_plan_import_fixes_the_state_case():
    to_add, _, _ = plan_import([make_parsed("TC-005", state="passed")], [], VALID_STATES)

    assert to_add[0]["state"] == "Passed"


def test_plan_import_reports_invalid_states_and_missing_steps():
    parsed = [make_parsed("TC-005", state="Done"), make_parsed("TC-006", steps=0, line=9)]
    to_add, _, invalid = plan_import(parsed, [], VALID_STATES)

    assert to_add == []
    assert "invalid state 'Done'" in invalid[0]
    assert "Line 9" in invalid[1]