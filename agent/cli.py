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

# Command: update an existing test case
@cli.command()
@click.argument("test_id")
def update_test(test_id):
    """Update an existing test case. Ex: python agent/cli.py update-test TC-001"""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    test = next((tc for tc in data["test_cases"] if tc["id"] == test_id), None)

    if test is None:
        click.echo(f"\n❌ Test case '{test_id}' not found.\n")
        return

    click.echo(f"\n✏️  Updating test case '{test_id}' — {test['title']}")
    click.echo("   Leave blank to keep the current value.\n")

    title = click.prompt(f"   Title", default=test["title"])
    area_path = click.prompt(f"   Area", default=test["area_path"])
    assigned_to = click.prompt(f"   Assigned to", default=test["assigned_to"])

    test["title"] = title
    test["area_path"] = area_path
    test["assigned_to"] = assigned_to

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("test_updated", test_id, f"Test case '{test_id}' updated")

    click.echo(f"\n✅ Test case '{test_id}' successfully updated!\n")

# Command: search test cases
@cli.command()
@click.option("--keyword", "-k", default=None, help="Search by keyword")
@click.option("--assignee", "-a", default=None, help="Search by assignee")
@click.option("--area", "-ar", default=None, help="Search by area")
@click.option("--state", "-s", default=None, help="Search by state")
def search(keyword, assignee, area, state):
    """Search test cases by different criteria."""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    results = data["test_cases"]

    if keyword:
        keyword_lower = keyword.lower()
        results = [
            tc for tc in results
            if keyword_lower in tc["title"].lower()
            or keyword_lower in tc["area_path"].lower()
            or keyword_lower in tc["assigned_to"].lower()
        ]

    if assignee:
        results = [
            tc for tc in results
            if assignee.lower() in tc["assigned_to"].lower()
        ]

    if area:
        results = [
            tc for tc in results
            if area.lower() in tc["area_path"].lower()
        ]

    if state:
        results = [
            tc for tc in results
            if state.lower() == tc["state"].lower()
        ]

    if not results:
        click.echo(f"\n❌ No test cases found.\n")
        return

    click.echo(f"\n🔍 Search results:\n")
    for tc in results:
        click.echo(f"  {tc['id']} | {tc['title']} | {tc['state']} | {tc['assigned_to']}")
    click.echo("")


# Command: show test cases statistics
@cli.command()
def stats():
    """Show test cases statistics."""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    total = len(data["test_cases"])
    states = {}
    for tc in data["test_cases"]:
        state = tc["state"]
        states[state] = states.get(state, 0) + 1

    click.echo(f"\n📊 Test Cases Statistics\n")
    click.echo(f"  Total:        {total}")
    for state, count in states.items():
        percentage = round((count / total) * 100)
        click.echo(f"  {state:<15} {count}  ({percentage}%)")
    click.echo("")

# Command: assign a test case to a team member
@cli.command()
@click.argument("test_id")
def assign(test_id):
    """Assign a test case to a team member. Ex: python agent/cli.py assign TC-001"""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    test = next((tc for tc in data["test_cases"] if tc["id"] == test_id), None)

    if test is None:
        click.echo(f"\n❌ Test case '{test_id}' not found.\n")
        return

    click.echo(f"\n👤 Assigning test case '{test_id}' — {test['title']}")
    click.echo(f"   Current assignee: {test['assigned_to']}\n")

    new_assignee = click.prompt("   New assignee")

    old_assignee = test["assigned_to"]
    test["assigned_to"] = new_assignee

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("test_assigned", test_id, f"Assigned from '{old_assignee}' to '{new_assignee}'")

    click.echo(f"\n✅ TC '{test_id}' assigned to '{new_assignee}'!\n")

# Command: search pull requests
@cli.command()
@click.option("--title", "-t", default=None, help="Search by title")
@click.option("--author", "-a", default=None, help="Search by author")
@click.option("--reviewer", "-r", default=None, help="Search by reviewer")
@click.option("--state", "-s", default="open", help="Search by state (open, closed, merged, all)")
def search_prs(title, author, reviewer, state):
    """Search pull requests on GitHub."""
    import subprocess as sp

    click.echo(f"\n🔍 Searching Pull Requests...\n")

    if state == "all":
        cmd = ["gh", "pr", "list", "--state", "open", "--json",
               "number,title,author,reviewRequests,state,url"]
        cmd2 = ["gh", "pr", "list", "--state", "closed", "--json",
                "number,title,author,reviewRequests,state,url"]
        result2 = sp.run(cmd2, capture_output=True, text=True)
    elif state == "merged":
        cmd = ["gh", "pr", "list", "--state", "closed", "--json",
               "number,title,author,reviewRequests,state,url,mergedAt"]
    else:
        cmd = ["gh", "pr", "list", "--state", state, "--json",
               "number,title,author,reviewRequests,state,url,mergedAt"]

    result = sp.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        click.echo(f"\n❌ Error connecting to GitHub: {result.stderr}\n")
        return

    import json as json_module
    prs = json_module.loads(result.stdout)
    if state == "all" and result2.returncode == 0:
        prs += json_module.loads(result2.stdout)
    elif state == "merged":
        prs = [pr for pr in prs if pr.get("mergedAt")]
    elif state == "closed":
        prs = [pr for pr in prs if not pr.get("mergedAt")]

    if not prs:
        click.echo(f"\n❌ No pull requests found.\n")
        return

    if title:
        prs = [pr for pr in prs if title.lower() in pr["title"].lower()]

    if author:
        prs = [pr for pr in prs if author.lower() in pr["author"]["login"].lower()]

    if reviewer:
        prs = [pr for pr in prs
               if any(reviewer.lower() in r["login"].lower()
               for r in pr.get("reviewRequests", []))]

    if not prs:
        click.echo(f"\n❌ No pull requests found with the given filters.\n")
        return

    click.echo(f"  {'#':<5} {'Title':<45} {'Author':<15} {'State':<10} URL")
    click.echo(f"  {'─'*5} {'─'*45} {'─'*15} {'─'*10} {'─'*40}")
    for pr in prs:
        number = f"#{pr['number']}"
        title_short = pr["title"][:43] + ".." if len(pr["title"]) > 43 else pr["title"]
        author_name = pr["author"]["login"][:13]
        pr_state = pr["state"]
        url = pr["url"]
        click.echo(f"  {number:<5} {title_short:<45} {author_name:<15} {pr_state:<10} {url}")
    click.echo("")

        
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