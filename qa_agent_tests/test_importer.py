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