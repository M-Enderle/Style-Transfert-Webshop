"""
Utility functions and classes.
"""

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
    """
    Product class.

    Parameters:
        pimage (Image.Image): The product image as a PIL Image object.
        ai_size (float): The size of the product image as a float.
        psize (str): The size of the product as a string.
        ptype (str): The type of the product as a string.
        pcolor (str): The color of the product as a string.
        pcount (int): The number of products as an integer.
    """

    def __init__(
        self,
        pimage: Image.Image,
        ai_size: float,
        psize: str,
        ptype: str,
        pcolor: str,
        pcount: int,
    ) -> None:
        """
        Initializes the Product class.
        """
        self.image = pimage
        self.ai_size = ai_size
        self.size = psize
        self.type = ptype
        self.color = pcolor
        self.count = pcount

    def __eq__(self, __value) -> bool:
        """
        Compares two Product objects.
        """
        return (
            not ImageChops.difference(self.image, __value.image).getbbox()
            and self.ai_size == __value.ai_size
            and self.size == __value.size
            and self.type == __value.type
            and self.color == __value.color
        )
