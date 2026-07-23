import questionary
import subprocess
import sys
import os

def run_command(command):
    """Runs a CLI command."""
    subprocess.run([sys.executable, "agent/cli.py"] + command)

def wait_for_menu():
    """Waits for the user to press Enter before returning to the menu."""
    input("\nPress Enter to return to the menu...")

def test_cases_menu():
    """Submenu for Test Cases."""
    while True:
        print("\n📋 Test Cases\n")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "👁️  View Test Cases",
                "🔍 Search Test Cases",
                "➕ Create Test Case",
                "✏️  Update Test Case",
                "👤 Assign Test Case",
                "📊 Stats",
                "📤 Export Test Cases History",
                "⬅️  Back"
            ]
        ).ask()

        if choice == "👁️  View Test Cases":
            run_command(["list-tests"])
            wait_for_menu()

        elif choice == "🔍 Search Test Cases":
            search_by = questionary.select(
                "Search by:",
                choices=[
                    "🔤 Keyword (searches everything)",
                    "👤 Assignee",
                    "📁 Area",
                    "🔵 State",
                ]
            ).ask()

            if search_by == "🔤 Keyword (searches everything)":
                value = questionary.text("Keyword:").ask()
                run_command(["search", "--keyword", value])

            elif search_by == "👤 Assignee":
                value = questionary.text("Assignee name:").ask()
                run_command(["search", "--assignee", value])

            elif search_by == "📁 Area":
                value = questionary.text("Area:").ask()
                run_command(["search", "--area", value])

            elif search_by == "🔵 State":
                value = questionary.select(
                    "Select state:",
                    choices=["Active", "Passed", "Failed", "Blocked", "In Progress"]
                ).ask()
                run_command(["search", "--state", value])

            wait_for_menu()

        elif choice == "➕ Create Test Case":
            run_command(["add-test"])
            wait_for_menu()

        elif choice == "✏️  Update Test Case":
            test_id = questionary.text("Test Case ID (e.g. TC-001):").ask()
            run_command(["update-test", test_id])
            wait_for_menu()

        elif choice == "👤 Assign Test Case":
            test_id = questionary.text("Test Case ID (e.g. TC-001):").ask()
            run_command(["assign", test_id])
            wait_for_menu()

        elif choice == "📊 Stats":
            run_command(["stats"])
            wait_for_menu()

        elif choice == "📤 Export Test Cases History":
            run_command(["export-tests-history"])
            wait_for_menu()

        elif choice == "⬅️  Back":
            break

def history_menu():
    """Submenu for History."""
    while True:
        print("\n📜 History\n")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "📜 View History",
                "📤 Export History",
                "⬅️  Back"
            ]
        ).ask()

        if choice == "📜 View History":
            run_command(["history"])
            wait_for_menu()

        elif choice == "📤 Export History":
            run_command(["export-history"])
            wait_for_menu()

        elif choice == "⬅️  Back":
            break

def create_pull_request():
    """Interactive flow to create a Pull Request."""

    print("\n🔀 Create Pull Request\n")

    platform = questionary.select(
        "Select platform:",
        choices=["GitHub", "GitLab", "Cancel"]
    ).ask()

    if platform == "Cancel":
        print("\n❌ PR creation cancelled.\n")
        return

    title = questionary.text("PR Title:").ask()
    if not title:
        print("\n❌ PR creation cancelled.\n")
        return

    template_path = ".github/pull_request_template.md"
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            template = f.read()
    else:
        template = "## Description\n\n## How to Test\n\n## Checklist\n"

    print("\n📝 PR Description (edit the template below):")
    print("💡 Tip: Press Option + Enter (Mac) or Alt + Enter (Windows) when finished.")
    print("─" * 50)
    input("Press Enter to open the description editor...")
    description = questionary.text(
        "Description:",
        default=template,
        multiline=True,
        instruction=""
    ).ask()

    if not description:
        print("\n❌ PR creation cancelled.\n")
        return

    confirm = questionary.select(
        "\nWhat would you like to do?",
        choices=["✅ Create Pull Request", "❌ Cancel"]
    ).ask()

    if confirm == "❌ Cancel":
        print("\n❌ PR creation cancelled.\n")
        return

    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True
    ).stdout.strip()

    if current_branch == "main":
        print("\n⚠️  You are on the 'main' branch. Please switch to a feature branch before creating a PR.")
        print("💡 Tip: Run 'git checkout -b feature/your-feature-name' to create a new branch.\n")
        return

    print("\n⏳ Preparing your Pull Request...\n")

    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", title])
    subprocess.run(["git", "push", "--set-upstream", "origin", current_branch])

    if platform == "GitHub":
        result = subprocess.run(
            ["gh", "pr", "create", "--title", title, "--body", description],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"\n✅ Pull Request created successfully!")
            print(f"🔗 {result.stdout.strip()}\n")
        else:
            print(f"\n❌ Error creating PR: {result.stderr}\n")

    elif platform == "GitLab":
        print("\n⚠️  GitLab integration coming soon.\n")

def pull_requests_menu():
    """Submenu for Pull Requests."""
    while True:
        print("\n🔀 Pull Requests\n")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "📋 View All PRs",
                "🔍 Search PRs",
                "➕ Create Pull Request",
                "⬅️  Back"
            ]
        ).ask()

        if choice == "📋 View All PRs":
            state = questionary.select(
                "Show PRs with state:",
                choices=["🟢 Open", "🔴 Closed", "🟣 Merged", "📋 All"]
            ).ask()

            state_map = {
                "🟢 Open": "open",
                "🔴 Closed": "closed",
                "🟣 Merged": "merged",
                "📋 All": "all"
            }

            run_command(["search-prs", "--state", state_map[state]])
            wait_for_menu()

        elif choice == "🔍 Search PRs":
            search_by = questionary.select(
                "Search by:",
                choices=[
                    "🔤 Title",
                    "👤 Author",
                    "👥 Reviewer",
                    "🔵 State",
                    "⬅️  Back"
                ]
            ).ask()

            if search_by == "⬅️  Back":
                continue

            if search_by == "🔤 Title":
                value = questionary.text("Title (min. 3 characters):").ask()
                run_command(["search-prs", "--title", value])

            elif search_by == "👤 Author":
                value = questionary.text("Author username:").ask()
                run_command(["search-prs", "--author", value])

            elif search_by == "👥 Reviewer":
                value = questionary.text("Reviewer username:").ask()
                run_command(["search-prs", "--reviewer", value])

            elif search_by == "🔵 State":
                value = questionary.select(
                    "Select state:",
                    choices=["🟢 Open", "🔴 Closed", "🟣 Merged", "📋 All"]
                ).ask()

                state_map = {
                    "🟢 Open": "open",
                    "🔴 Closed": "closed",
                    "🟣 Merged": "merged",
                    "📋 All": "all"
                }

                run_command(["search-prs", "--state", state_map[value]])

            wait_for_menu()

        elif choice == "➕ Create Pull Request":
            create_pull_request()
            wait_for_menu()

        elif choice == "⬅️  Back":
            break


def main():
    while True:
        print("\n🤖 QA Agent\n")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "📋 Test Cases",
                "🗺️  Roadmap",
                "📜 History",
                "🤖 Ask AI",
                "🔀 Pull Requests",
                "❌ Exit"
            ]
        ).ask()

        if choice == "📋 Test Cases":
            test_cases_menu()

        elif choice == "🗺️  Roadmap":
            run_command(["roadmap"])
            wait_for_menu()

        elif choice == "📜 History":
            history_menu()

        elif choice == "🤖 Ask AI":
            question = questionary.text("What would you like to ask?").ask()
            run_command(["ask", question])
            wait_for_menu()

        elif choice == "🔀 Pull Requests":
            pull_requests_menu()

        elif choice == "❌ Exit":
            print("\n👋 Goodbye!\n")
            break

if __name__ == "__main__":
    main()