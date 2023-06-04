""" Utility functions for the project. """

import os
from pathlib import Path

import requests
import toml
from PIL import Image


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent.parent.parent


def load_user_toml() -> dict:
    """Loads user.toml file."""
    if os.path.exists(get_project_root() / "user.toml"):
        return toml.load(get_project_root() / "user.toml")
    return toml.load(get_project_root() / "default.toml")


def transfer(content_img, style_img):
    """Transfer style from style image to content image."""

    # TODO Josh: Implement this function, see notebook

    retult_img = None

    return content_img


class Cart:
    # TODO Josh: Implement this class
    pass
