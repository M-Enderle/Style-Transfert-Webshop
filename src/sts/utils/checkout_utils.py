"""
This module contains all the functions needed to generate a payment link via
the stripe API.
"""

import pandas as pd
import stripe

from sts.utils.utils import Product, load_user_toml

user = load_user_toml()


def generate_payment_link(checkout_items):
    """
    This function generates a payment link via the stripe API. All of the items
    the customer added to the car are forwarded to stripe to then generate the
    payment link.
    :params:
        checkout_items: The already sorted items having to be paid
    """

    stripe.api_key = user["stripe"]["api_key"]

    items = {
        "Shirt": "price_1NIwaDESoYzI2jIeLtaeYFB1",
        "Hoodie": "price_1NIwbjESoYzI2jIerbxUMCYb",
        "shipping": "price_1NJL88ESoYzI2jIeOdv5xcY6",
    }

    order = []

    for item in checkout_items:
        copy_item = {"Product": item["product_type"], "Amount": item["Amount"]}
        order.append(copy_item)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": items[order_item["Product"]],
                "quantity": order_item["Amount"],
            }
            for order_item in order
        ],
        mode="payment",
        success_url="https://www.metritests.com/metrica/MobileRedirectPage.aspx",
        cancel_url="https://www.metritests.com/metrica/MobileRedirectPage.aspx",
    )
    return session.url, session


def generate_cart(cart_items):
    """
    Adding information about shipping cost
    """
    shipping_cost = {
        "Productname": "Shipping",
        "Amount": "1",
        "Size": "via DHL",
        "Price Total": "5.49 €",
        "product_type": "shipping",
    }

    checkout_items = []
    for item in cart_items:
        item: Product
        price = 25.0 if item.type == "Hoodie" else 15.0
        new_item = {
            "Productname": f"{item.type} - {item.color}",
            "product_type": item.type,
            "Amount": item.count,
            "Size": item.size,
            "Price Item": str(price) + " €",
            "Price Total": str(price) + " €",
        }
        checkout_items.append(new_item)

    checkout_items.append(shipping_cost)
    checkout_table = pd.DataFrame(checkout_items)
    checkout_table = checkout_table.fillna("")
    total_sum = checkout_table["Price Total"].str.replace(" €", "").astype(float).sum()
    return (
        total_sum,
        checkout_items,
        checkout_table[["Productname", "Amount", "Size", "Price Item", "Price Total"]],
    )
