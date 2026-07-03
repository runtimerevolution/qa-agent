import click
import json
import os

# Path to knowledge base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_CASES_PATH = os.path.join(BASE_DIR, "knowledge_base", "test_cases", "test_cases.json")
HISTORY_PATH = os.path.join(BASE_DIR, "knowledge_base", "history.json")

def log_event(event_type, test_id, details):
    """Logs an event to the project history."""
    from datetime import datetime

    with open(HISTORY_PATH, "r") as f:
        history = json.load(f)

    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": event_type,
        "test_id": test_id,
        "details": details
    }

    history["events"].append(event)

    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# Main entry point
@click.group()
def cli():
    """QA Agent — QA Assistant for your team."""
    pass

# Command: list all test cases
@cli.command()
def list_tests():
    """List all available test cases."""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    click.echo("\n📋 Available test cases:\n")
    for tc in data["test_cases"]:
        click.echo(f"  {tc['id']} | {tc['title']} | {tc['state']} | {tc['assigned_to']}")
    click.echo("")

# Command: show details of a specific test case
@cli.command()
@click.argument("test_id")
def show(test_id):
    """Show details of a specific test case. Ex: python agent/cli.py show TC-001"""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    test = next((tc for tc in data["test_cases"] if tc["id"] == test_id), None)

    if test is None:
        click.echo(f"\n❌ Test case '{test_id}' not found.\n")
        return

    click.echo(f"\n📋 {test['id']} — {test['title']}")
    click.echo(f"   State:       {test['state']}")
    click.echo(f"   Assigned to: {test['assigned_to']}")
    click.echo(f"   Area:        {test['area_path']}")
    click.echo(f"\n   Steps:")
    for step in test["steps"]:
        click.echo(f"\n   {step['step']}. {step['action']}")
        click.echo(f"      ✅ Expected: {step['expected']}")
    click.echo("")

# Command: update the state of a test case
@cli.command()
@click.argument("test_id")
@click.argument("new_state")
def update_state(test_id, new_state):
    """Update the state of a test case. Ex: python agent/cli.py update-state TC-001 Passed"""
    valid_states = ["Active", "Passed", "Failed", "Blocked", "In Progress"]

    if new_state not in valid_states:
        click.echo(f"\n❌ Invalid state. Available states: {', '.join(valid_states)}\n")
        return

    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    test = next((tc for tc in data["test_cases"] if tc["id"] == test_id), None)

    if test is None:
        click.echo(f"\n❌ Test case '{test_id}' not found.\n")
        return

    old_state = test["state"]
    test["state"] = new_state

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("state_change", test_id, f"{old_state} → {new_state}")

    click.echo(f"\n✅ TC '{test_id}' updated: {old_state} → {new_state}\n")

# Command: add a new test case
@cli.command()
def add_test():
    """Add a new test case to the database."""
    click.echo("\n➕ Add new Test Case\n")

    test_id = click.prompt("   ID (ex: TC-003)")
    title = click.prompt("   Title")
    area_path = click.prompt("   Area (ex: Project/Login)")
    assigned_to = click.prompt("   Assigned to")

    steps = []
    step_num = 1
    click.echo("\n   Add the test steps (leave action blank to finish):\n")

    while True:
        action = click.prompt(f"   Step {step_num} — Action", default="")
        if action == "":
            break
        expected = click.prompt(f"   Step {step_num} — Expected result")
        steps.append({
            "step": step_num,
            "action": action,
            "expected": expected
        })
        step_num += 1

    new_test = {
        "id": test_id,
        "work_item_type": "Test Case",
        "title": title,
        "area_path": area_path,
        "assigned_to": assigned_to,
        "state": "Active",
        "steps": steps
    }

    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    data["test_cases"].append(new_test)

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("test_created", test_id, f"Test case '{title}' created")

    click.echo(f"\n✅ Test case '{test_id}' successfully added!\n")

# Command: show the team roadmap
@cli.command()
def roadmap():
    """Show the current team roadmap."""
    roadmap_path = os.path.join(BASE_DIR, "knowledge_base", "roadmap", "roadmap.md")

    with open(roadmap_path, "r") as f:
        content = f.read()

    click.echo("\n🗺️  Team roadmap:\n")
    click.echo(content)

# Command: show the project history
@cli.command()
def history():
    """Show the project change history."""
    with open(HISTORY_PATH, "r") as f:
        data = json.load(f)

    if not data["events"]:
        click.echo("\n📜 No events recorded yet.\n")
        return

    click.echo("\n📜 Project history:\n")
    for event in data["events"]:
        click.echo(f"  {event['timestamp']} | {event['test_id']} | {event['details']}")
    click.echo("")

# Command: export change history to Markdown
@cli.command()
def export_history():
    """Export the project history to a Markdown file."""
    with open(HISTORY_PATH, "r") as f:
        data = json.load(f)

    if not data["events"]:
        click.echo("\n📜 No events to export yet.\n")
        return

    export_path = os.path.join(BASE_DIR, "knowledge_base", "history.md")

    with open(export_path, "w") as f:
        f.write("# Project Change History\n\n")

        current_date = None
        for event in data["events"]:
            date, time = event["timestamp"].split(" ")

            if date != current_date:
                current_date = date
                f.write(f"\n## {date}\n\n")

            f.write(f"- {time} | {event['test_id']} | {event['details']}\n")

    click.echo(f"\n✅ History exported to knowledge_base/history.md\n")

# Command: export test cases history to Markdown
@cli.command()
def export_tests_history():
    """Export the list of created test cases to a Markdown file."""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    if not data["test_cases"]:
        click.echo("\n📋 No test cases to export yet.\n")
        return

    export_path = os.path.join(BASE_DIR, "knowledge_base", "test_cases_history.md")

    with open(export_path, "w") as f:
        f.write("# Test Cases History\n\n")
        f.write(f"Project: {data['project']}\n")
        f.write(f"Last updated: {data['last_updated']}\n\n")

        for tc in data["test_cases"]:
            f.write(f"- {tc['id']} | {tc['title']} | {tc['state']} | {tc['assigned_to']}\n")

    click.echo(f"\n✅ Test cases history exported to knowledge_base/test_cases_history.md\n")

if __name__ == "__main__":
    cli()