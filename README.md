# QA Agent 🤖

Internal command-line tool (CLI) to help the QA team manage their work,
especially during the transition to test automation.

Developed at Runtime Revolution.

---

## Requirements

- Python 3.x
- pip

---

## Installation

**1. Clone or copy the project to your machine**

**2. Navigate to the project folder:**
```bash
cd qa-agent
```

**3. Create and activate the virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**4. Install dependencies:**
```bash
pip install click
```

---

## Available Commands

### 📋 List all test cases
```bash
python agent/cli.py list-tests
```

### 🔍 View details of a specific test case
```bash
python agent/cli.py show TC-001
```

### ✏️ Update the state of a test case
```bash
python agent/cli.py update-state TC-001 Passed
```
Available states: `Active` `Passed` `Failed` `Blocked` `In Progress`

### ➕ Add a new test case
```bash
python agent/cli.py add-test
```

### 🗺️ View the team roadmap
```bash
python agent/cli.py roadmap
```

### 📜 View the change history in the terminal
```bash
python agent/cli.py history
```

### 📤 Export change history to Markdown
```bash
python agent/cli.py export-history
```
Generates file: `knowledge_base/history.md`

### 📤

📁 qa-agent/
├── 📁 agent/
│   └── 📄 cli.py                        ← CLI source code
├── 📁 knowledge_base/
│   ├── 📁 test_cases/
│   │   └── 📄 test_cases.json           ← test cases database
│   ├── 📁 roadmap/
│   │   └── 📄 roadmap.md                ← team roadmap
│   ├── 📁 guidelines/
│   │   └── 📄 guidelines.md             ← QA best practices
│   ├── 📄 history.json                  ← history in JSON (internal use)
│   ├── 📄 history.md                    ← exported change history
│   └── 📄 test_cases_history.md         ← exported test cases history
└── 📁 venv/                             ← virtual environment (do not share)

---

## Important Notes

- Always activate the virtual environment before using the tool: `source venv/bin/activate`
- Never delete a test case — change the state to `Blocked` if no longer applicable
- Update `roadmap.md` whenever a step is completed
- The `venv/` folder should not be shared or pushed to Git


## Changelog

- 2026-06-30 — Initial project setup

## Requirements

> Already listed above, but for AI integration add:
- [Ollama](https://ollama.com) installed and running
- Llama 3.2 model pulled locally

## AI Integration Setup

**1. Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**2. Start the Ollama server:**
```bash
ollama serve
```

**3. Pull the Llama 3.2 model:**
```bash
ollama pull llama3.2
```

**4. Install the Python Ollama library:**
```bash
pip install ollama
```

> Note: The `ollama serve` terminal must remain active while using the `ask` command.

## AI Command

### 🤖 Ask the AI agent a question
```bash
python agent/cli.py ask "Your question here"
```

The agent reads the entire Knowledge Base (test cases, roadmap, guidelines) before answering, ensuring responses are always contextualised to your project.

**Examples:**
```bash
python agent/cli.py ask "What should I test next?"
python agent/cli.py ask "What test cases do we have for the Login module?"
python agent/cli.py ask "What are the team guidelines for automation?"
```