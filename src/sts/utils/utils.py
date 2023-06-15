import os
from pathlib import Path
import toml


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent.parent.parent


def load_user_toml() -> dict:
    """Loads user.toml file."""
    if os.path.exists(get_project_root() / "user.toml"):
        return toml.load(get_project_root() / "user.toml")
    return toml.load(get_project_root() / "default.toml")


class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        """Adds an item to the cart."""
        self.items.append(item)

    def remove_item(self, item):
        """Removes an item from the cart."""
        if item in self.items:
            self.items.remove(item)

    def clear_cart(self):
        """Clears all items from the cart."""
        self.items = []

    def get_items(self):
        """Returns a list of items in the cart."""
        return self.items

    def get_total_items(self):
        """Returns the total number of items in the cart."""
        return len(self.items)

    def calculate_total_price(self):
        """Calculates the total price of items in the cart."""
        total_price = 0
        # Assuming each item has a 'price' attribute
        for item in self.items:
            total_price += item.price
        return total_price
