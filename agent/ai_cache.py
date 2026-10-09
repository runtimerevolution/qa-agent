"""Simple file-based cache for AI answers."""

import hashlib
import json
import os


def make_key(provider, model, prompt):
    """Creates a unique key for a prompt sent to a specific provider and model."""
    text = f"{provider}|{model}|{prompt}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache(cache_path):
    """Reads the cache file. Returns an empty cache if it does not exist or is broken."""
    if not os.path.exists(cache_path):
        return {}

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def get_cached_answer(cache_path, key):
    """Returns the saved answer for this key, or None if there is none."""
    return load_cache(cache_path).get(key)


def save_answer(cache_path, key, answer):
    """Saves an answer in the cache."""
    cache = load_cache(cache_path)
    cache[key] = answer

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def clear_cache(cache_path):
    """Deletes the cache file. Returns True if there was something to delete."""
    if os.path.exists(cache_path):
        os.remove(cache_path)
        return True
    return False