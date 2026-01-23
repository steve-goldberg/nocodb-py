"""Configuration management for NocoDB CLI.

Config priority (highest to lowest):
1. Command-line flags
2. Environment variables
3. Config file (~/.nocodbrc)
4. Built-in defaults
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class Config:
    """NocoDB CLI configuration."""

    url: str = ""
    token: str = ""
    base_id: str = ""
    profile: str = "default"

    def is_valid(self) -> bool:
        """Check if configuration has required fields."""
        return bool(self.url and self.token)

    def get_missing_fields(self) -> list[str]:
        """Return list of missing required fields."""
        missing = []
        if not self.url:
            missing.append("url")
        if not self.token:
            missing.append("token")
        return missing


def get_config_path() -> Path:
    """Get the config file path."""
    env_path = os.environ.get("NOCODB_CONFIG")
    if env_path:
        return Path(env_path)

    local_config = Path(".nocodbrc")
    if local_config.exists():
        return local_config

    return Path.home() / ".nocodbrc"


def load_config_file(config_path: Optional[Path] = None) -> dict:
    """Load configuration from TOML file."""
    path = config_path or get_config_path()

    if not path.exists():
        return {}

    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def load_config(
    url: Optional[str] = None,
    token: Optional[str] = None,
    base_id: Optional[str] = None,
    profile: Optional[str] = None,
    config_path: Optional[Path] = None,
) -> Config:
    """Load configuration from all sources with proper priority.

    Priority (highest to lowest):
    1. Function arguments (CLI flags)
    2. Environment variables
    3. Profile from config file
    4. Default section from config file
    """
    file_config = load_config_file(config_path)

    selected_profile = (
        profile
        or os.environ.get("NOCODB_PROFILE")
        or "default"
    )

    defaults = file_config.get("default", {})
    profile_config = file_config.get("profiles", {}).get(selected_profile, {})

    merged = {**defaults, **profile_config}

    return Config(
        url=(
            url
            or os.environ.get("NOCODB_URL")
            or merged.get("url", "")
        ),
        token=(
            token
            or os.environ.get("NOCODB_TOKEN")
            or merged.get("token", "")
        ),
        base_id=(
            base_id
            or os.environ.get("NOCODB_BASE_ID")
            or merged.get("base_id", "")
        ),
        profile=selected_profile,
    )


def create_example_config() -> str:
    """Return example config file content."""
    return """# NocoDB CLI Configuration
# Save this file as ~/.nocodbrc

[default]
url = "http://localhost:8080"
# token should be in NOCODB_TOKEN env var for security
# token = "your-api-token"
# base_id = "your-default-base-id"

# [profiles.prod]
# url = "https://nocodb.example.com"
# base_id = "prod_base_id"

# [profiles.dev]
# url = "http://localhost:8080"
# base_id = "dev_base_id"
"""
