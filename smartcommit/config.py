"""
Loads configuration for SmartCommit.

Priority order (highest wins):
1. Environment variable (GEMINI_API_KEY)
2. .env file in current directory
3. ~/.smartcommit.toml (user-level config, optional overrides)
"""

import os
import tomllib
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file if present in current working directory
load_dotenv()

USER_CONFIG_PATH = Path.home() / ".smartcommit.toml"


@dataclass
class Config:
    gemini_api_key: str
    model_name: str = "gemini-2.0-flash"
    max_diff_chars: int = 6000  # truncate huge diffs so we don't blow token limits


def _load_user_toml() -> dict:
    """Read ~/.smartcommit.toml if it exists. Returns {} if not found."""
    if not USER_CONFIG_PATH.exists():
        return {}
    with open(USER_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def load_config() -> Config:
    toml_data = _load_user_toml()

    api_key = os.getenv("GEMINI_API_KEY") or toml_data.get("gemini_api_key")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found.\n"
            "Set it in a .env file (GEMINI_API_KEY=your_key) "
            "or in ~/.smartcommit.toml, or as an environment variable."
        )

    model_name = toml_data.get("model_name", "gemini-3.6-flash")
    max_diff_chars = toml_data.get("max_diff_chars", 6000)

    return Config(
        gemini_api_key=api_key,
        model_name=model_name,
        max_diff_chars=max_diff_chars,
    )
