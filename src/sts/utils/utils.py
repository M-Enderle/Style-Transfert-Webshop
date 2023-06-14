import os
from pathlib import Path
import stripe
import time

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
    

    def generate_payment_link(checkout_items):
        with open("api_key.conf", "r") as f:
            stripe.api_key = f.read()

        items = {
            "shirt": "price_1NIwaDESoYzI2jIeLtaeYFB1",
            "hoodie": "price_1NIwbjESoYzI2jIerbxUMCYb",
            "black": "price_1NIwYnESoYzI2jIeRGmnZbVs"
        }

        order = []

        for item in checkout_items:
            copy_item = {'Product': item['product_type'], 'Amount': item['Amount']}
            order.append(copy_item)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': items[order_item['item']],
                    'quantity': order_item['quantity'],
                } for order_item in order
            ],
            mode='payment',
            success_url='https://www.metritests.com/metrica/MobileRedirectPage.aspx', # We have to find some way to close the tab
            cancel_url='https://www.metritests.com/metrica/MobileRedirectPage.aspx',  # We have to find some way to close the tab
        )

        timeout_after = time.time() + 60 * 2  # 2 minutes from now

        while session.payment_status != 'paid':
            if time.time() > timeout_after:
                # Timeout Logik == Cancelled Logik
                print("Timeout / Cancelled")
                break
            session = stripe.checkout.Session.retrieve(session.id)
            # We wait
        else:
            # Paid Logik
            print("Payment status: %s" % session.payment_status)


    