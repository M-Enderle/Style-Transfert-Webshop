import pandas as pd

import stripe
from sts.utils.utils import load_user_toml, Product

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
        "shirt": "price_1NIwaDESoYzI2jIeLtaeYFB1",
        "hoodie": "price_1NIwbjESoYzI2jIerbxUMCYb",
        "black": "price_1NIwYnESoYzI2jIeRGmnZbVs",
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
        # We have to find some way to close the tab
        cancel_url="https://www.metritests.com/metrica/MobileRedirectPage.aspx",
        # We have to find some way to close the tab
    )
    return session.url, session


def generate_cart(cart_items):
    # Adding information about shipping cost.
    shipping_cost = {
        "Productname": "Shipping",
        "Amount": "1",
        "Size": "via DHL",
        "Price Total": "5.49 €",
        "product_type": "shipping",
    }

    # Clustering and storing items the customer added to his cart.
    checkout_items = []
    for item in cart_items:
        already_added = False
        size = item.size
        product = item.product

        for checkout_item in checkout_items:
            if checkout_items:
                if (
                    checkout_item["Size"] == size
                    and checkout_item["product_type"] == product
                ):
                    checkout_item["Amount"] += 1
                    sum = int(checkout_item["Price Item"].replace(" €", "")) * int(
                        checkout_item["Amount"]
                    )
                    checkout_item["Price Total"] = str(sum) + " €"
                    already_added = True

        if not already_added:
            product_name = (
                "T-Shirt - white"
                if product == "shirt"
                else "Hoodie - white"
                if product == "hoodie"
                else "T-Shirt - black"
            )
            amount = 1
            image_paths = {
                "hoodie": "src/sts/utils/images/white_hoodie.png",
                "shirt": "src/sts/utils/images/white_tshirt.png",
                "black": "src/sts/utils/images/black_tshirt.png",
            }

            single_price = item["price"]
            new_item = {
                "Productname": product_name,
                "product_type": product,
                "Amount": amount,
                "Size": size,
                "Price Item": str(single_price) + " €",
                "Price Total": str(single_price) + " €",
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
