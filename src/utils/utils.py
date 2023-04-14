from pathlib import Path

import toml


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent.parent


def load_user_toml() -> dict:
    """Loads user.toml file."""
    return toml.load(get_project_root() / "user.toml")
