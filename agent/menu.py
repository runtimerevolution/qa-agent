import questionary
import subprocess
import sys

def run_command(command):
    """Runs a CLI command."""
    subprocess.run([sys.executable, "agent/cli.py"] + command)

def wait_for_menu():
    """Waits for the user to press Enter before returning to the menu."""
    input("\nPress Enter to return to the menu...")

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

        elif choice == "❌ Exit":
            print("\n👋 Goodbye!\n")
            break

if __name__ == "__main__":
    main()