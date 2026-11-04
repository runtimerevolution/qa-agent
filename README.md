# QA Agent 🤖

Internal command-line tool (CLI) to help the QA team manage their work, especially during the transition to test automation.

With the QA Agent you can manage test cases, follow the team roadmap, keep a change history, search and create Pull Requests, run Playwright tests and ask an AI assistant questions about your project, all from the terminal.

Developed at Runtime Revolution.

---

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Interactive Menu](#interactive-menu)
- [Commands](#commands)
- [AI Features](#ai-features)
- [Check Installation (doctor)](#-check-installation-doctor)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Important Notes](#important-notes)
- [Changelog](#changelog)

---

## Requirements

| Requirement | Needed for |
|-------------|------------|
| Python 3.10 or newer | Everything |
| Git | Everything |
| [GitHub CLI](https://cli.github.com) (`gh`), logged in | Pull Request features |
| [Ollama](https://ollama.com) | AI features (optional) |

The QA Agent works on **macOS** and **Windows**.

---

## Installation

**1. Clone the project:**
```bash
git clone https://github.com/runtimerevolution/qa-agent.git
cd qa-agent
```

**2. Create and activate the virtual environment:**

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install the dependencies:**
```bash
pip install click questionary
```

For the AI features, also install:
```bash
pip install ollama
```

**4. Create your configuration file:**

macOS / Linux:
```bash
cp config.example.json config.json
```

Windows:
```bash
copy config.example.json config.json
```

Then open `config.json` and fill in the values for your project (see [Configuration](#configuration)).

**5. Check that everything is ready:**
```bash
python -m agent.cli doctor
```

The `doctor` command tells you if anything is missing and how to fix it.

---

## Configuration

### What it is

Each person has their own `config.json` file, with the settings for their project and their computer. It is never shared through Git, so you can change it freely without affecting anyone else.

The file `config.example.json` is the template: copy it to create your own.

### Fields

| Field | What it does | Example |
|-------|--------------|---------|
| `project` | Name of the project you are testing | `"Team Allocator"` |
| `platform` | Git platform used by the project | `"GitHub"` |
| `available_platforms` | Platforms shown in the menu | `["GitHub", "GitLab", "Bitbucket"]` |
| `base_branch` | Main branch of the project | `"main"` |
| `ai_enabled` | Turns the AI features on or off | `true` |
| `ai_cache_enabled` | Saves AI answers to reuse them (see [Saved answers](#saved-answers-cache)) | `true` |
| `ai_provider` | Which AI provider to use | `"ollama"` |
| `ai_models` | The model to use for each provider | see below |

Example of the AI section:
```json
"ai_enabled": true,
"ai_cache_enabled": true,
"ai_provider": "ollama",
"ai_models": {
  "ollama": "llama3.2",
  "claude": "claude-sonnet-5",
  "openai": ""
}
```

### Technical notes

- `config.json` is listed in `.gitignore` and is not tracked by Git.
- The configuration is read by `load_config()` in `agent/cli.py`. If the file is missing or broken, safe default values are used, so the tool never crashes because of it. Run `doctor` to find out if your file has a formatting error.
- The AI settings are read through `get_ai_settings()`, which returns whether the AI is on, the provider and the model for that provider. Older config files with a single `ai_model` field still work, but it is recommended to update to the structure above.
- API keys are **never** stored in `config.json`. See [AI providers](#ai-providers).

---

## Interactive Menu

The easiest way to use the QA Agent. Instead of typing commands, you choose options from a menu.

```bash
python agent/menu.py
```

Navigate with the **arrow keys** and press **Enter** to select an option.

| Menu | Options |
|------|---------|
| 📋 **Test Cases** | View, search, create, generate with AI, update, assign, run one Playwright test, run multiple tests, delete, stats, export history |
| 🗺️ **Roadmap** | View, add item, move item, mark as completed, remove item |
| 📜 **History** | View history, export history |
| 🤖 **Ask AI** | Ask a question, ask again (ignoring saved answers), clear saved answers |
| 🔀 **Pull Requests** | Choose the platform, then view, search or create Pull Requests |
| 🩺 **Check Installation** | Checks that everything the QA Agent needs is installed and configured |
| ❌ **Exit** | Exits the menu |

### Creating a Pull Request from the menu

Go to **🔀 Pull Requests → GitHub → ➕ Create Pull Request** and follow the steps:

1. Write the PR title.
2. Fill in the description. The PR template opens already filled in. Press **Option + Enter** (Mac) or **Alt + Enter** (Windows) when finished.
3. Confirm the creation.
4. If you have uncommitted changes, choose which files to include: move with the arrow keys, select with **Space**, and confirm with **Enter**. Only the selected files are included in the PR.

You need to be on a feature branch, not on `main`. GitLab and Bitbucket are prepared but not available yet.

---

## Commands

All the menu options are also available as commands. They are useful if you prefer typing, or want to use the QA Agent in scripts.

```bash
python -m agent.cli <command>
```

To see all commands and their help:
```bash
python -m agent.cli --help
```

### 📋 Test Cases

| Command | What it does |
|---------|--------------|
| `list-tests` | Lists all test cases. Add `--json` for a machine-readable list (used by the menu) |
| `show TC-001` | Shows the details and steps of a test case |
| `add-test` | Adds a new test case, step by step |
| `update-test TC-001` | Updates the title, area, assignee or Playwright file of a test case |
| `update-state TC-001 Passed` | Changes the state of a test case |
| `assign TC-001` | Assigns a test case to a team member |
| `delete-test TC-001` | Deletes a test case, after confirmation |
| `search` | Searches test cases (see options below) |
| `stats` | Shows statistics by state |
| `export-tests-history` | Exports the test cases list to `knowledge_base/test_cases_history.md` |

Available states: `Active` `Passed` `Failed` `Blocked` `In Progress`

Search options:
```bash
python -m agent.cli search --keyword login
python -m agent.cli search --assignee Diogo
python -m agent.cli search --area Project/Login
python -m agent.cli search --state Failed
python -m agent.cli run-tests --id TC-001 --id TC-003  # run specific test cases
```

### 🗺️ Roadmap

| Command | What it does |
|---------|--------------|
| `roadmap` | Shows the team roadmap |
| `roadmap-add todo "Item"` | Adds an item to a section |
| `roadmap-move "Item" inprogress` | Moves an item to another section |
| `roadmap-complete "Item"` | Marks an item as completed |
| `roadmap-remove "Item"` | Removes an item, after confirmation |

Available sections: `inprogress` `todo` `backlog`

### 📜 History

| Command | What it does |
|---------|--------------|
| `history` | Shows the change history |
| `export-history` | Exports the history to `knowledge_base/history.md` |

Every change to a test case is recorded automatically.

### 🎭 Playwright

| Command | What it does |
|---------|--------------|
| `run-test TC-001` | Runs the Playwright test linked to one test case and updates its state |
| `run-tests` | Runs the Playwright tests of all test cases that match the filters (see below) |

Add `--simulate` to any of them to simulate the run without opening a browser (demo mode).

A test case needs a `playwright_file` linked to it to be run. You can add one with `update-test`.

**Running multiple tests**

`run-tests` uses the same filters as `search`, and they can be combined:

```bash
python -m agent.cli run-tests --state Failed          # run the tests that failed again
python -m agent.cli run-tests --area Project/Login    # run all tests from an area
python -m agent.cli run-tests --assignee Diogo        # run all tests assigned to someone
python -m agent.cli run-tests --keyword checkout      # run all tests matching a keyword
python -m agent.cli run-tests --area Login --state Failed
```

Before running, it shows which tests will run and which will be skipped because they have no Playwright test linked, and asks for confirmation. Without filters, it runs **all** tests, and the confirmation defaults to "no". At the end, it shows a summary and updates the state of each test case.

In the menu: **📋 Test Cases → 🧪 Run Multiple Tests**. Choose **☑️ Choose from a list** to pick the tests one by one. Test cases without a Playwright test are shown but cannot be selected.

**Technical notes**

- The filters live in `filter_test_cases()` and the test execution in `execute_test()`, both in `agent/cli.py`. They are shared by `search`, `run-test` and `run-tests`.
- Tests run one at a time, so the result of each test case is known. Each run calls pytest with `sys.executable`, so the Python from the virtual environment is always used.

### 🔀 Pull Requests

```bash
python -m agent.cli search-prs --state open
python -m agent.cli search-prs --title login
python -m agent.cli search-prs --author username
python -m agent.cli search-prs --reviewer username
```

Available states: `open` `closed` `merged` `all`

### 🤖 AI

| Command | What it does |
|---------|--------------|
| `ask "Your question"` | Asks the AI a question about your project |
| `ask "Your question" --no-cache` | Asks the AI again, ignoring the saved answer |
| `generate-test` | Generates a test case with AI, step by step |
| `clear-cache` | Deletes all saved AI answers |

### 🩺 Installation

| Command | What it does |
|---------|--------------|
| `doctor` | Checks that everything the QA Agent needs is installed and configured |

---

## AI Features

### What they do

The QA Agent can use AI in two ways:

- **Ask questions** about your project. The AI reads the test cases, the roadmap and the guidelines before answering, so its answers are always about your project.
- **Generate test cases** from a short description of a feature.

**The AI is optional.** Everything else in the QA Agent works without it. If your computer feels slow with the AI running, or you don't need it, you can simply turn it off.

**Examples:**
```bash
python -m agent.cli ask "What should I test next?"
python -m agent.cli ask "What test cases do we have for the Login module?"
python -m agent.cli ask "What are the team guidelines for automation?"
```

### Turning the AI on or off

In your `config.json`:
```json
"ai_enabled": false
```

With the AI off, the AI commands explain how to turn it back on, and everything else keeps working normally.

### Setting up Ollama

Ollama runs the AI locally, on your own computer. Your data never leaves the company, and it is free.

**1. Install Ollama** from [ollama.com](https://ollama.com).

**2. Start the Ollama server** and keep this terminal open while using the AI:
```bash
ollama serve
```

**3. Download the model** set in your `config.json`:
```bash
ollama pull llama3.2
```

**4. Install the Python library:**
```bash
pip install ollama
```

Tip: if your computer is less powerful, you can choose a smaller model in `ai_models`.

### AI providers

| Provider | Status | Requirement |
|----------|--------|-------------|
| `ollama` | ✅ Available | Ollama installed and running |
| `claude` | 🔜 Coming soon | Anthropic API key |
| `openai` | 🔜 Coming soon | OpenAI API key |

To change the provider, change `ai_provider` in your `config.json`. The model for that provider is taken from `ai_models` automatically.

> ⚠️ **Privacy:** with Ollama, everything stays on your computer. With Claude or OpenAI, your questions and project information (test cases, roadmap, guidelines) are sent to an external service.

### Saved answers (cache)

When you ask a question, the answer is saved on your computer. If you ask the same question again, the saved answer appears instantly (marked with 💾), without running the AI again.

- If the test cases, roadmap or guidelines change, the AI is asked again automatically, so answers are never out of date.
- If you change the provider or the model, the AI is asked again too.
- Only `ask` uses saved answers. `generate-test` always creates a new suggestion.

To control it:
- Get a fresh answer: `ask "Your question" --no-cache`, or **🔄 Ask Again** in the menu
- Delete all saved answers: `clear-cache`, or **🧹 Clear Saved Answers** in the menu
- Turn it off: `"ai_cache_enabled": false` in `config.json`

### Technical notes

- All AI calls go through a single function, `ask_ai()` in `agent/cli.py`. Commands do not know which provider is configured. Activating a new provider only requires filling in its block in `ask_ai()`.
- API keys will be read from environment variables (`ANTHROPIC_API_KEY` and `OPENAI_API_KEY`), never from `config.json`.
- The cache lives in `agent/ai_cache.py` and is saved in `.ai_cache.json`, next to `config.json`. The file is in `.gitignore`, so each person keeps their own answers.
- Each answer is stored under a SHA-256 key built from the provider, the model and the full prompt (including the Knowledge Base content). Any change to these produces a different key, which is how outdated answers are avoided.
- Errors from the AI are never saved in the cache.

---

## 🩺 Check Installation (`doctor`)

### What it does

Checks that everything the QA Agent needs is installed and configured on your computer, and tells you how to fix anything that is missing. Run it right after installing the QA Agent, or whenever something is not working as expected.

```bash
python -m agent.cli doctor
```

It is also available in the interactive menu under **🩺 Check Installation**.

### Result icons

| Icon | Meaning |
|------|---------|
| ✅ | Everything is fine |
| ⚠️ | The QA Agent works, but some features are limited |
| ❌ | Must be fixed before the QA Agent can work |

### What is checked

| Check | If it fails |
|-------|-------------|
| Python version (3.10 or newer) | ❌ The QA Agent cannot run |
| `config.json` exists and is valid | ❌ The QA Agent cannot read its settings |
| Git is installed | ❌ Branch and PR features cannot work |
| GitHub CLI is installed and logged in | ⚠️ PR features are unavailable |
| AI is ready (for Ollama: installed, running and model downloaded) | ⚠️ AI features are unavailable |

If the AI is turned off in `config.json`, the AI check shows ✅, since this is a choice and not a problem.

### Technical notes

- All checks live in `agent/doctor.py`. Each check is a small function that returns a status (`ok`, `warning` or `error`) and a message.
- Installed programs are detected with `shutil.which`, and commands are run with `subprocess` using a 10-second timeout, so the checks work the same way on macOS and Windows.
- The AI check receives the settings already read by `get_ai_settings()` in `agent/cli.py`, so the configuration is read in a single place.
- To add a new check, write a new function in `agent/doctor.py` and add it to the list in `run_doctor()`.

---

## Project Structure

```
qa-agent/
├── .github/
│   └── pull_request_template.md   ← template used for every PR
├── agent/
│   ├── cli.py                     ← all commands
│   ├── menu.py                    ← interactive menu
│   ├── doctor.py                  ← installation checks
│   └── ai_cache.py                ← saved AI answers
├── knowledge_base/
│   ├── test_cases/
│   │   └── test_cases.json        ← test cases database
│   ├── roadmap/
│   │   └── roadmap.md             ← team roadmap
│   ├── guidelines/
│   │   └── guidelines.md          ← QA best practices
│   ├── history.json               ← change history (internal use)
│   ├── history.md                 ← exported change history
│   └── test_cases_history.md      ← exported test cases list
├── tests/                         ← Playwright test files
├── config.example.json            ← configuration template
├── config.json                    ← your configuration (personal, not in Git)
├── .ai_cache.json                 ← your saved AI answers (personal, not in Git)
└── venv/                          ← virtual environment (personal, not in Git)
```

### Technical notes

- Test cases and history are stored in **JSON**, because the code reads and changes them. The roadmap and guidelines are stored in **Markdown**, because people read and edit them.
- All files are read and written as UTF-8, so accents and emojis work the same way on macOS and Windows.
- Git and GitHub CLI are called through `subprocess`, which keeps the tool light and avoids extra libraries.

---

## Contributing

- **One PR per change.** Create the branch before writing any code.
- **Branch names** start with the type of change:
  - `feature/` for new features
  - `fix/` for bug fixes
  - `docs/` for documentation only
- **Nothing hardcoded.** Anything that changes between projects goes in `config.json` (and in `config.example.json` as a template).
- **Code and documentation in English.**
- **Fill in the PR template**, including how to test the change.
- **Run `doctor`** and test your change on the menu before opening the PR.

---

## Important Notes

- Always activate the virtual environment before using the tool.
- Never delete a test case that was already used: change its state to `Blocked` if it no longer applies.
- Update the roadmap whenever a step is completed.
- Never share your `config.json`, `.ai_cache.json` or `venv/` folder, and never push them to Git.

---

## Changelog
- **2026-10-26**
  - `run-tests` can run specific test cases with `--id`
  - New **☑️ Choose from a list** option in **🧪 Run Multiple Tests**
  - `list-tests --json` returns the test cases in JSON
- **2026-10-20** 
  - New `run-tests` command to run several tests at once, using filters
  - New **🧪 Run Multiple Tests** option in the Test Cases menu
  - `run-test` now always uses the Python from the virtual environment
- **2026-10-20**
  - New `doctor` command to check the installation
  - AI can be turned on or off, and each provider has its own model
  - Saved answers (cache) for `ask`, with `--no-cache` and `clear-cache`
  - New **🤖 Ask AI** submenu
  - Choose which files to include when creating a PR from the menu
  - Windows compatibility: screen clearing and UTF-8 files
  - `config.json` is no longer tracked by Git
- **2026-06-30** — Initial project setup