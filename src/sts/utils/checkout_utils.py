import time

import stripe


def generate_payment_link(checkout_items):
    """
    This function generates a payment link via the stripe API. All of the items
    the customer added to the car are forwarded to stripe to then generate the
    payment link.
    :params:
        checkout_items: The already sorted items having to be paid
    """
    with open("src/sts/utils/api_key.conf", "r") as f:
        stripe.api_key = f.read()

    items = {
        "shirt": "price_1NIwaDESoYzI2jIeLtaeYFB1",
        "hoodie": "price_1NIwbjESoYzI2jIerbxUMCYb",
        "black": "price_1NIwYnESoYzI2jIeRGmnZbVs",
        "shipping": "price_1NJL88ESoYzI2jIeOdv5xcY6"
    }

    order = []

    for item in checkout_items:
        copy_item = {"Product": item["product_type"], "Amount": item["Amount"]}
        order.append(copy_item)

    print(order)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": items[order_item["Product"]],
                "quantity": order_item["Amount"],
            } for order_item in order
        ],
        mode="payment",
        success_url="https://www.metritests.com/metrica/MobileRedirectPage.aspx",
        # We have to find some way to close the tab
        cancel_url="https://www.metritests.com/metrica/MobileRedirectPage.aspx",
        # We have to find some way to close the tab
    )
    return session.url, session

def pay_articles(session):
    timeout_after = time.time() + 60 * 60  # an hour from now

    while session.payment_status != "paid":
        if time.time() > timeout_after:
            # Timeout Logik == Cancelled Logik
            return False
            print("Timeout / Cancelled")
            break
        session = stripe.checkout.Session.retrieve(session.id)
        # We wait
    else:
        # Paid Logik
        # TODO amelie
        return True
        print("Payment status: %s" % session.payment_status)