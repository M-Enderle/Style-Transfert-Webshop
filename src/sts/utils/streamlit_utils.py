# https://github.com/mkhorasani/Streamlit-Authenticator

import base64
import io

import requests
import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image

import sts.app.database as db
from sts.utils.utils import load_user_toml

session = db.session
user_data = load_user_toml()


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


def transfer(content_img: Image, style_img: Image):
    """Transfer style from style image to content image."""

    # convert to RBG if RGBA
    if content_img.mode == "RGBA":
        content_img = content_img.convert("RGB")
    if style_img.mode == "RGBA":
        style_img = style_img.convert("RGB")

    # Convert content_img to bytes-like object
    content_buffer = io.BytesIO()
    content_img.save(content_buffer, format="JPEG")
    content_img_bytes = content_buffer.getvalue()

    # Convert style_img to bytes-like object
    style_buffer = io.BytesIO()
    style_img.save(style_buffer, format="JPEG")
    style_img_bytes = style_buffer.getvalue()

    # Encode as base64 strings
    content_img_64 = base64.b64encode(content_img_bytes).decode("utf-8")
    style_img_64 = base64.b64encode(style_img_bytes).decode("utf-8")

    files = [("content_img", content_img_64), ("style_img", style_img_64)]

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


def is_logged_in():
    """Returns True if user is logged in."""
    if "username" in st.session_state and st.session_state.username is not None:
        return True
    return False
