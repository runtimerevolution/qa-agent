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
    click.echo("\n➕ Add new Test Case")
    click.echo("   💡 Type 'cancel' at any point to abort.\n")

    test_id = click.prompt("   ID (ex: TC-003)")
    if test_id.lower() == "cancel":
        click.echo("\n❌ Test case creation cancelled.\n")
        return

    title = click.prompt("   Title")
    if title.lower() == "cancel":
        click.echo("\n❌ Test case creation cancelled.\n")
        return

    area_path = click.prompt("   Area (ex: Project/Login)")
    if area_path.lower() == "cancel":
        click.echo("\n❌ Test case creation cancelled.\n")
        return

    assigned_to = click.prompt("   Assigned to")
    if assigned_to.lower() == "cancel":
        click.echo("\n❌ Test case creation cancelled.\n")
        return

    steps = []
    step_num = 1
    click.echo("\n   Add the test steps (leave action blank to finish):\n")

    while True:
        action = click.prompt(f"   Step {step_num} — Action", default="")
        if action.lower() == "cancel":
            click.echo("\n❌ Test case creation cancelled.\n")
            return
        if action == "":
            break
        expected = click.prompt(f"   Step {step_num} — Expected result")
        if expected.lower() == "cancel":
            click.echo("\n❌ Test case creation cancelled.\n")
            return
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
        "playwright_file": "",
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
    click.echo("   Leave blank to keep the current value.")
    click.echo("   💡 Type 'cancel' at any point to abort.\n")

    title = click.prompt(f"   Title", default=test["title"])
    if title.lower() == "cancel":
        click.echo("\n❌ Update cancelled.\n")
        return

    area_path = click.prompt(f"   Area", default=test["area_path"])
    if area_path.lower() == "cancel":
        click.echo("\n❌ Update cancelled.\n")
        return

    assigned_to = click.prompt(f"   Assigned to", default=test["assigned_to"])
    if assigned_to.lower() == "cancel":
        click.echo("\n❌ Update cancelled.\n")
        return

    playwright_file = click.prompt(f"   Playwright file", default=test.get("playwright_file", ""))
    if playwright_file.lower() == "cancel":
        click.echo("\n❌ Update cancelled.\n")
        return

    test["title"] = title
    test["area_path"] = area_path
    test["assigned_to"] = assigned_to
    test["playwright_file"] = playwright_file

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
    click.echo(f"   Current assignee: {test['assigned_to']}")
    click.echo("   💡 Type 'cancel' to abort.\n")

    new_assignee = click.prompt("   New assignee")

    if new_assignee.lower() == "cancel":
        click.echo("\n❌ Assignment cancelled.\n")
        return

    old_assignee = test["assigned_to"]
    test["assigned_to"] = new_assignee

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("test_assigned", test_id, f"Assigned from '{old_assignee}' to '{new_assignee}'")

    click.echo(f"\n✅ TC '{test_id}' assigned to '{new_assignee}'!\n")

# Command: delete a test case
@cli.command()
@click.argument("test_id")
def delete_test(test_id):
    """Delete a test case from the database. Ex: python agent/cli.py delete-test TC-001"""
    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    test = next((tc for tc in data["test_cases"] if tc["id"] == test_id), None)

    if test is None:
        click.echo(f"\n❌ Test case '{test_id}' not found.\n")
        return

    click.echo(f"\n🗑️  You are about to delete the following test case:")
    click.echo(f"   {test['id']} | {test['title']} | {test['state']} | {test['assigned_to']}\n")

    confirm = click.confirm("   Are you sure you want to delete this test case?", default=False)

    if not confirm:
        click.echo(f"\n❌ Deletion cancelled.\n")
        return

    data["test_cases"] = [tc for tc in data["test_cases"] if tc["id"] != test_id]

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("test_deleted", test_id, f"Test case '{test['title']}' deleted")

    click.echo(f"\n✅ Test case '{test_id}' successfully deleted!\n")


# Command: run a playwright test
@cli.command()
@click.argument("test_id")
@click.option("--simulate", is_flag=True, default=False, help="Simulate test run without browser")
def run_test(test_id, simulate):
    """Run a Playwright test for a specific test case. Ex: python agent/cli.py run-test TC-001"""
    import subprocess as sp
    import time

    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    test = next((tc for tc in data["test_cases"] if tc["id"] == test_id), None)

    if test is None:
        click.echo(f"\n❌ Test case '{test_id}' not found.\n")
        return

    playwright_file = test.get("playwright_file")

    if not playwright_file:
        click.echo(f"\n❌ No Playwright test linked to '{test_id}'.\n")
        click.echo(f"   Add a 'playwright_file' field to the test case in test_cases.json.\n")
        return

    click.echo(f"\n🎭 Running Playwright test for '{test_id}' — {test['title']}\n")

    if simulate:
        click.echo(f"   📄 Test file: {playwright_file}")
        click.echo(f"   🌐 Browser: Chromium")
        click.echo(f"   ⏳ Running steps:\n")
        for step in test["steps"]:
            click.echo(f"      Step {step['step']}: {step['action']}")
            time.sleep(0.5)
            click.echo(f"      ✅ {step['expected']}\n")
        new_state = "Passed"
        click.echo(f"\n✅ Test passed!\n")
    else:
        result = sp.run(
            ["python", "-m", "pytest", playwright_file, "-v"],
            capture_output=False
        )
        if result.returncode == 0:
            new_state = "Passed"
            click.echo(f"\n✅ Test passed!\n")
        else:
            new_state = "Failed"
            click.echo(f"\n❌ Test failed!\n")

    test["state"] = new_state

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("test_run", test_id, f"Playwright test ran — result: {new_state}")

    click.echo(f"📝 State updated to '{new_state}' automatically.\n")

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
               "number,title,author,reviewRequests,state,url,mergedAt"]
        cmd2 = ["gh", "pr", "list", "--state", "closed", "--json",
                "number,title,author,reviewRequests,state,url,mergedAt"]
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

    if title:
        prs = [pr for pr in prs if title.lower() in pr["title"].lower()]

    if author:
        prs = [pr for pr in prs if author.lower() in pr["author"]["login"].lower()]

    if reviewer:
        prs = [pr for pr in prs
               if any(reviewer.lower() in r["login"].lower()
               for r in pr.get("reviewRequests", []))]

    if not prs:
        click.echo(f"\n❌ No pull requests found.\n")
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

# Command: add item to roadmap
@cli.command()
@click.argument("section")
@click.argument("item")
def roadmap_add(section, item):
    """Add an item to the roadmap. Sections: inprogress, todo, backlog"""
    roadmap_path = os.path.join(BASE_DIR, "knowledge_base", "roadmap", "roadmap.md")

    section_map = {
        "inprogress": "### 🟢 In Progress",
        "todo": "### 🟡 To Do",
        "backlog": "### 🔴 Backlog"
    }

    if section not in section_map:
        click.echo(f"\n❌ Invalid section. Use: inprogress, todo, backlog\n")
        return

    with open(roadmap_path, "r") as f:
        content = f.read()

    section_header = section_map[section]
    content = content.replace(section_header, f"{section_header}\n- {item}")

    with open(roadmap_path, "w") as f:
        f.write(content)

    click.echo(f"\n✅ Item added to '{section}': {item}\n")

# Command: move item in roadmap
@cli.command()
@click.argument("item")
@click.argument("to_section")
def roadmap_move(item, to_section):
    """Move an item to another section. Sections: inprogress, todo, backlog"""
    roadmap_path = os.path.join(BASE_DIR, "knowledge_base", "roadmap", "roadmap.md")

    section_map = {
        "inprogress": "### 🟢 In Progress",
        "todo": "### 🟡 To Do",
        "backlog": "### 🔴 Backlog"
    }

    if to_section not in section_map:
        click.echo(f"\n❌ Invalid section. Use: inprogress, todo, backlog\n")
        return

    with open(roadmap_path, "r") as f:
        content = f.read()

    if f"- {item}" not in content:
        click.echo(f"\n❌ Item '{item}' not found in roadmap.\n")
        return

    content = content.replace(f"- {item}\n", "")
    section_header = section_map[to_section]
    content = content.replace(section_header, f"{section_header}\n- {item}")

    with open(roadmap_path, "w") as f:
        f.write(content)

    click.echo(f"\n✅ Item moved to '{to_section}': {item}\n")

# Command: mark roadmap item as completed
@cli.command()
@click.argument("item")
def roadmap_complete(item):
    """Mark a roadmap item as completed."""
    roadmap_path = os.path.join(BASE_DIR, "knowledge_base", "roadmap", "roadmap.md")

    with open(roadmap_path, "r") as f:
        content = f.read()

    if f"- {item}" not in content:
        click.echo(f"\n❌ Item '{item}' not found in roadmap.\n")
        return

    content = content.replace(f"- {item}\n", "")
    content = content.replace("### ✅ Completed", f"### ✅ Completed\n- {item}")

    with open(roadmap_path, "w") as f:
        f.write(content)

    click.echo(f"\n✅ Item marked as completed: {item}\n")

# Command: remove roadmap item
@cli.command()
@click.argument("item")
def roadmap_remove(item):
    """Remove an item from the roadmap."""
    roadmap_path = os.path.join(BASE_DIR, "knowledge_base", "roadmap", "roadmap.md")

    with open(roadmap_path, "r") as f:
        content = f.read()

    if f"- {item}" not in content:
        click.echo(f"\n❌ Item '{item}' not found in roadmap.\n")
        return

    confirm = click.confirm(f"   Are you sure you want to remove '{item}'?", default=False)

    if not confirm:
        click.echo(f"\n❌ Removal cancelled.\n")
        return

    content = content.replace(f"- {item}\n", "")

    with open(roadmap_path, "w") as f:
        f.write(content)

    click.echo(f"\n✅ Item removed from roadmap: {item}\n")

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

# Command: generate test case with AI
@cli.command()
def generate_test():
    """Generate a test case automatically using AI."""
    import ollama

    click.echo("\n🤖 AI Test Case Generator")
    click.echo("   💡 Type 'cancel' at any point to abort.\n")

    feature = click.prompt("   Describe the feature to test")
    if feature.lower() == "cancel":
        click.echo("\n❌ Generation cancelled.\n")
        return

    area = click.prompt("   Area (ex: Project/Login)")
    if area.lower() == "cancel":
        click.echo("\n❌ Generation cancelled.\n")
        return

    assigned_to = click.prompt("   Assigned to")
    if assigned_to.lower() == "cancel":
        click.echo("\n❌ Generation cancelled.\n")
        return

    prompt = f"""
You are a QA expert. Generate a test case for the following feature:

Feature: {feature}
Area: {area}

Respond ONLY in this exact JSON format, nothing else:
{{
    "title": "test case title",
    "steps": [
        {{
            "step": 1,
            "action": "action description",
            "expected": "expected result"
        }}
    ]
}}

Generate between 3 and 5 steps. Be specific and technical.
"""

    click.echo("\n⏳ Generating test case...\n")

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    import json as json_module
    try:
        raw = response["message"]["content"]
        start = raw.find("{")
        end = raw.rfind("}") + 1
        generated = json_module.loads(raw[start:end])
    except Exception:
        click.echo("\n❌ Error generating test case. Please try again.\n")
        return

    click.echo(f"\n📋 Generated Test Case:\n")
    click.echo(f"   Title: {generated['title']}")
    click.echo(f"\n   Steps:")
    for step in generated["steps"]:
        click.echo(f"\n   {step['step']}. {step['action']}")
        click.echo(f"      ✅ Expected: {step['expected']}")

    click.echo("")
    confirm = click.confirm("   Save this test case?", default=True)

    if not confirm:
        click.echo("\n❌ Test case not saved.\n")
        return

    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)

    existing_ids = [tc["id"] for tc in data["test_cases"]]
    numbers = [int(id.replace("TC-", "")) for id in existing_ids if id.startswith("TC-")]
    next_id = f"TC-{str(max(numbers) + 1).zfill(3)}" if numbers else "TC-001"

    new_test = {
        "id": next_id,
        "work_item_type": "Test Case",
        "title": generated["title"],
        "area_path": area,
        "assigned_to": assigned_to,
        "state": "Active",
        "playwright_file": "",
        "steps": generated["steps"]
    }

    data["test_cases"].append(new_test)

    with open(TEST_CASES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_event("test_created", next_id, f"Test case '{generated['title']}' generated by AI")

    click.echo(f"\n✅ Test case '{next_id}' saved successfully!\n")

# Command: ask a question to the AI agent
@cli.command()
@click.argument("question")
def ask(question):
    """Ask a question to the AI agent based on the Knowledge Base."""
    import ollama

    with open(TEST_CASES_PATH, "r") as f:
        test_cases = json.load(f)

    roadmap_path = os.path.join(BASE_DIR, "knowledge_base", "roadmap", "roadmap.md")
    with open(roadmap_path, "r") as f:
        roadmap = f.read()

    guidelines_path = os.path.join(BASE_DIR, "knowledge_base", "guidelines", "guidelines.md")
    with open(guidelines_path, "r") as f:
        guidelines = f.read()

    context = f"""
You are a QA assistant. Answer based only on the following project information:

TEAM ROADMAP:
{roadmap}

QA GUIDELINES:
{guidelines}

TEST CASES:
{json.dumps(test_cases, indent=2)}

Answer the following question: {question}
"""

    click.echo("\n🤖 Thinking...\n")

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": context}]
    )

    click.echo(f"{response['message']['content']}\n")

if __name__ == "__main__":
    cli()