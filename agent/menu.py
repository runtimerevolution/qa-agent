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

def create_pull_request():
    """Interactive flow to create a Pull Request."""

    print("\n🔀 Create Pull Request\n")

    # Select platform
    platform = questionary.select(
        "Select platform:",
        choices=["GitHub", "GitLab", "Cancel"]
    ).ask()

    if platform == "Cancel":
        print("\n❌ PR creation cancelled.\n")
        return

    # PR Title
    title = questionary.text("PR Title:").ask()
    if not title:
        print("\n❌ PR creation cancelled.\n")
        return

    # PR Description (pre-filled with template)
    template_path = ".github/pull_request_template.md"
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            template = f.read()
    else:
        template = "## Description\n\n## How to Test\n\n## Checklist\n"

    print("\n📝 PR Description (edit the template and save when done):")
    print("─" * 50)
    description = questionary.text(
        "Description:",
        default=template,
        multiline=True
    ).ask()

    if not description:
        print("\n❌ PR creation cancelled.\n")
        return

    # Confirmation
    confirm = questionary.select(
        "\nWhat would you like to do?",
        choices=["✅ Create Pull Request", "❌ Cancel"]
    ).ask()

    if confirm == "❌ Cancel":
        print("\n❌ PR creation cancelled.\n")
        return

    # git add, commit, push and create PR
    print("\n⏳ Preparing your Pull Request...\n")

    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", title])
    subprocess.run(["git", "push"])

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

def main():
    while True:
        print("\n🤖 QA Agent\n")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "📋 View Test Cases",
                "➕ Create Test Case",
                "🗺️  View Roadmap",
                "📜 View History",
                "📤 Export History",
                "📤 Export Test Cases History",
                "🤖 Ask AI",
                "🔀 Create Pull Request",
                "❌ Exit"
            ]
        ).ask()

        if choice == "📋 View Test Cases":
            run_command(["list-tests"])
            wait_for_menu()

        elif choice == "➕ Create Test Case":
            run_command(["add-test"])
            wait_for_menu()

        elif choice == "🗺️  View Roadmap":
            run_command(["roadmap"])
            wait_for_menu()

        elif choice == "📜 View History":
            run_command(["history"])
            wait_for_menu()

        elif choice == "📤 Export History":
            run_command(["export-history"])
            wait_for_menu()

        elif choice == "📤 Export Test Cases History":
            run_command(["export-tests-history"])
            wait_for_menu()

        elif choice == "🤖 Ask AI":
            question = questionary.text("What would you like to ask?").ask()
            run_command(["ask", question])
            wait_for_menu()

        elif choice == "🔀 Create Pull Request":
            create_pull_request()
            wait_for_menu()

        elif choice == "❌ Exit":
            print("\n👋 Goodbye!\n")
            break

if __name__ == "__main__":
    main()