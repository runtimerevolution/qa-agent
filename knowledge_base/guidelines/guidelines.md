# QA Guidelines — Automation Best Practices

## Test Case Structure
- Each test must have a unique ID (ex: TC-001)
- The title must be clear and descriptive
- Each step must have an action and an expected result
- The state must be updated after each execution

## Available Test Case States
- **Active** → test created but not yet executed
- **Passed** → test executed successfully
- **Failed** → test executed but errors were found
- **Blocked** → test cannot be executed (external dependency)
- **In Progress** → test under development

## Team Rules
- Never delete a test case — change the state to "Blocked" if no longer applicable
- Always assign a responsible person (field "assigned_to")
- Update `last_updated` in the JSON file after any changes
- Commit Knowledge Base changes at the end of each day

## Project Folder Structure
- `knowledge_base/test_cases/` → JSON files with test cases
- `knowledge_base/roadmap/` → team roadmap in Markdown
- `knowledge_base/guidelines/` → this file and other best practices
- `agent/` → CLI source code