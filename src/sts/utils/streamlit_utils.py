# https://github.com/mkhorasani/Streamlit-Authenticator

import base64
import io
import runpod
import time

import stripe
import requests
import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image, ImageDraw
from functools import lru_cache
import numpy as np
import sts.app.database as db
from sts.utils.utils import load_user_toml

session = db.session
user_data = load_user_toml()
BLACK_SHIRT = "src/sts/utils/images/black_tshirt.png"
WHITE_SHIRT = "src/sts/utils/images/white_tshirt.png"
WHITE_HOODIE = "src/sts/utils/images/white_hoodie.png"


@lru_cache
def overlay_image(strg, input_image, array_shape, is_circle=False, size=None):
    input_image = np.frombuffer(input_image, np.uint8)
    input_image = input_image.reshape(array_shape)
    input_image = Image.fromarray(input_image)

    if size is None:
        size = 0.25  # Default size: 25% of the smaller dimension

    if strg == "shirt":
        source_image = Image.open(WHITE_SHIRT)
    elif strg == "black":
        source_image = Image.open(BLACK_SHIRT)
    elif strg == "hoodie":
        source_image = Image.open(WHITE_HOODIE)
    else:
        raise EnvironmentError("Something went wrong calling overlay_image()")

    source_image = source_image.convert(
        "RGBA"
    )  # Convert to RGBA for transparency support
    input_image = input_image.convert("RGBA")
    # Set the x & y to the center of the background image
    width, height = int(input_image.width * size), int(input_image.height * size)
    x = int(source_image.width // 2 - width // 2)
    y = int(source_image.height // 2 - height // 2 - source_image.height * 0.12)
    input_image = input_image.resize((width, height))

    if is_circle:
        mask = Image.new("L", input_image.size, 0)
        draw = ImageDraw.Draw(mask)
        center = input_image.width // 2, input_image.height // 2
        radius = int(min(input_image.size)) // 2
        draw.ellipse(
            (
                center[0] - radius,
                center[1] - radius,
                center[0] + radius,
                center[1] + radius,
            ),
            fill=255,
        )
        source_image.paste(input_image, (x, y), mask=mask)
    else:
        source_image.paste(input_image, (x, y))

    # Save the output as a PNG image
    source_image.save("output.png", "PNG")

    return source_image


def get_authenticator() -> stauth.Authenticate:
    """
    Returns a streamlit_authenticator.Authenticate object
    """

    credentials = {
        "usernames": {
            "test": {
                "name": "test",
                "password": "$2b$12$WUXOCZmZqU0HTbggJ4hIBuCutUdQQo3xHWtafRkHtcjbo.TlboHq.",
                "email": "test@test.com",
            }
        }
    }

    return stauth.Authenticate(
        credentials=credentials,
        cookie_name=user_data["stauth"]["cookie_name"],
        key=user_data["stauth"]["cookie_secret_key"],
        cookie_expiry_days=user_data["stauth"]["cookie_expiry_days"],
    )


def convert_img_to_base64(img) -> str:
    """
    Converts an image to base64 string.
    """

    result_bytes = io.BytesIO()
    img.save(result_bytes, format="JPEG")
    result_bytes.seek(0)
    result_base64 = base64.b64encode(result_bytes.getvalue()).decode("utf-8")
    return result_base64


def convert_base64_to_img(base64_str: str):
    """
    Converts a base64 string to an image.
    """

    img = Image.open(io.BytesIO(base64.b64decode(base64_str)))
    return img


def transfer(content_img, style_img):
    """Transfer style from style image to content image."""

    content_img = content_img.convert("RGB")
    style_img = style_img.convert("RGB")

    content_img = convert_img_to_base64(content_img)
    style_img = convert_img_to_base64(style_img)

    if load_user_toml()["runpod"]["use"] == "true":
        runpod.api_key = load_user_toml()["runpod"]["api_key"]
        endpoint = runpod.Endpoint(load_user_toml()["runpod"]["endpoint"])

        data = {
            "content_img": content_img,
            "style_img": style_img,
            "resize_to": 512,
        }

        run_request = endpoint.run(
            data,
        )

        with st.spinner("Transferring style..."):
            result = run_request.output()

        result_image = convert_base64_to_img(result["result_image"])
        return result_image

    else:
        files = [("content_img", content_img), ("style_img", style_img)]

        try:
            with st.spinner("Transferring style..."):
                response = requests.post("http://localhost:8000/transfer", files=files)
        except requests.exceptions.ConnectionError:
            st.error("ConnectionError: Make sure the server is running.")
            return None

        retult_img = Image.open(
            io.BytesIO(base64.b64decode(response.json()["result_image"]))
        )

        return retult_img


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
    pay_articles(session)
    return session.url

def pay_articles(session):
    timeout_after = time.time() + 60 * 60  # 5 minutes from now

    while session.payment_status != "paid":
        if time.time() > timeout_after:
            # Timeout Logik == Cancelled Logik
            print("Timeout / Cancelled")
            break
        session = stripe.checkout.Session.retrieve(session.id)
        # We wait
    else:
        # Paid Logik
        # TODO amelie
        print("Payment status: %s" % session.payment_status)
