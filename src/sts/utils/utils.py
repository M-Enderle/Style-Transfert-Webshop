import os
from pathlib import Path

import toml
from PIL import Image, ImageChops


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent.parent.parent


def get_module_root() -> Path:
    """Returns module root folder."""
    return Path(__file__).parent.parent


def load_user_toml() -> dict:
    """Loads user.toml file."""
    if os.path.exists(get_project_root() / "user.toml"):
        return toml.load(get_project_root() / "user.toml")
    return toml.load(get_project_root() / "default.toml")


class Product:
    def __init__(
        self,
        pimage: Image.Image,
        ai_size: float,
        psize: str,
        ptype: str,
        pcolor: str,
        pcount: int,
    ) -> None:
        self.image = pimage
        self.ai_size = ai_size
        self.size = psize
        self.type = ptype
        self.color = pcolor
        self.count = pcount

    def __eq__(self, __value) -> bool:
        return (
            not ImageChops.difference(self.image, __value.image).getbbox()
            and self.ai_size == __value.ai_size
            and self.size == __value.size
            and self.type == __value.type
            and self.color == __value.color
        )
