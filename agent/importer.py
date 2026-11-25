"""Reads test cases from a CSV file with one row per step (like the Azure DevOps export)."""

import csv

# Default column names, the same as the Azure DevOps export.
# Each team can change them with "import_columns" in config.json.
DEFAULT_COLUMNS = {
    "id": "ID",
    "title": "Title",
    "area": "Area Path",
    "assigned_to": "Assigned To",
    "state": "State",
    "step_action": "Step Action",
    "step_expected": "Step Expected",
}

# Without these columns, there is nothing to import.
REQUIRED_COLUMNS = ["title", "step_action"]


def detect_delimiter(sample):
    """Returns the column separator used in the file: ',' or ';'."""
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;").delimiter
    except csv.Error:
        return ","


def cell(row, columns, key):
    """Returns the value of one column in a row, without extra spaces."""
    return (row.get(columns[key]) or "").strip()


def parse_csv(path, columns):
    """Reads a CSV file and returns (test_cases, problems)."""
    test_cases = []
    problems = []
    current = None

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        reader = csv.DictReader(f, delimiter=detect_delimiter(sample))

        missing = [
            columns[key] for key in REQUIRED_COLUMNS
            if columns[key] not in (reader.fieldnames or [])
        ]
        if missing:
            return [], [f"Missing columns: {', '.join(missing)}"]

        for line_number, row in enumerate(reader, start=2):
            title = cell(row, columns, "title")
            action = cell(row, columns, "step_action")

            if title:
                current = {
                    "id": cell(row, columns, "id"),
                    "title": title,
                    "area_path": cell(row, columns, "area"),
                    "assigned_to": cell(row, columns, "assigned_to"),
                    "state": cell(row, columns, "state") or "Active",
                    "steps": [],
                    "line": line_number,
                }
                test_cases.append(current)
            elif not action:
                continue
            elif current is None:
                problems.append(f"Line {line_number}: step without a test case above it")
                continue

            if action:
                current["steps"].append({
                    "step": len(current["steps"]) + 1,
                    "action": action,
                    "expected": cell(row, columns, "step_expected"),
                })

    return test_cases, problems