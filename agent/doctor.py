"""Installation checks for the QA Agent (the 'doctor' command)."""

import json
import os
import sys

# Minimum Python version supported by the QA Agent.
MIN_PYTHON = (3, 10)

# Possible results of each check.
OK = "ok"
ERROR = "error"
WARNING = "warning"

ICONS = {OK: "✅", ERROR: "❌", WARNING: "⚠️ "}


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


def run_doctor(config_path):
    """Run all checks and return a list of (status, message) results."""
    return [
        check_python(),
        check_config(config_path),
    ]