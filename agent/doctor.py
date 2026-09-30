"""Installation checks for the QA Agent (the 'doctor' command)."""

import json
import os
import sys
import shutil
import subprocess

# Minimum Python version supported by the QA Agent.
MIN_PYTHON = (3, 10)

# Possible results of each check.
OK = "ok"
ERROR = "error"
WARNING = "warning"

ICONS = {OK: "✅", ERROR: "❌", WARNING: "⚠️ "}

def is_installed(program):
    """Return True if a program is available on this computer."""
    return shutil.which(program) is not None


def run_command(command):
    """Run a command quietly. Return (success, output)."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return False, ""

def check_python():
    """Check that the Python version is supported."""
    current = (sys.version_info.major, sys.version_info.minor)
    version = f"{current[0]}.{current[1]}"

    if current >= MIN_PYTHON:
        return OK, f"Python {version}"

    minimum = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    return ERROR, f"Python {version} is too old → install Python {minimum} or newer"


def check_config(config_path):
    """Check that config.json exists and is valid JSON."""
    if not os.path.exists(config_path):
        return ERROR, "config.json not found → copy config.example.json to config.json"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        return ERROR, f"config.json has a formatting error (line {e.lineno}) → fix it and try again"

    return OK, "config.json found"

def check_git():
    """Check that Git is installed."""
    if is_installed("git"):
        return OK, "Git installed"
    return ERROR, "Git not found → install it from https://git-scm.com"


def check_github_cli():
    """Check that the GitHub CLI is installed and logged in."""
    if not is_installed("gh"):
        return WARNING, "GitHub CLI not found → install it from https://cli.github.com (needed for PR features)"

    logged_in, _ = run_command(["gh", "auth", "status"])
    if not logged_in:
        return WARNING, "GitHub CLI not logged in → run: gh auth login"

    return OK, "GitHub CLI installed and logged in"


def check_ai(config):
    """Check that the configured AI provider is ready to use."""
    provider = config.get("ai_provider", "").lower()
    model = config.get("ai_model", "")

    if provider == "ollama":
        if not is_installed("ollama"):
            return WARNING, "Ollama not found → install it from https://ollama.com (only needed for AI features)"

        running, output = run_command(["ollama", "list"])
        if not running:
            return WARNING, "Ollama is not running → run: ollama serve"

        if model not in output:
            return WARNING, f"Model '{model}' not downloaded → run: ollama pull {model}"

        return OK, f"AI ready ({provider} / {model})"

    if provider in ("claude", "openai"):
        return WARNING, f"AI provider '{provider}' is not available yet → set 'ai_provider' to 'ollama' in config.json"

    return WARNING, f"Unknown AI provider '{provider}' → use: ollama, claude or openai"


def run_doctor(config_path, config):
    """Run all checks and return a list of (status, message) results."""
    return [
        check_python(),
        check_config(config_path),
        check_git(),
        check_github_cli(),
        check_ai(config),
    ]