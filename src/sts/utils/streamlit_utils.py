# https://github.com/mkhorasani/Streamlit-Authenticator

import base64
import io

import requests
import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image

import sts.app.database as db
from sts.utils.utils import load_user_toml

user_data = load_user_toml()


def get_authenticator() -> stauth.Authenticate:
    """
    Returns a streamlit_authenticator.Authenticate object
    """
    session = db.create_session()
    users = session.query(db.User).all()
    credentials: dict = {"usernames": {}}
    for user in users:
        credentials["usernames"][user.username] = {
            "password": user.password_hash,
            "email": user.email,
            "name": user.name,
        }

    session.close()
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


def display_register(auth: stauth.Authenticate):
    """
    This page is displayed, when the user clicks on the Register Tab.
    Here the user can enter his personal information and try to register
    in the WebApp.
    """
    session = db.create_session()
    
    
    register_user_form = st.form("Register user")
    register_user_form.subheader("Register to access the app")
    new_email = register_user_form.text_input("Email")
    new_username = register_user_form.text_input("Username").lower()
    new_name = register_user_form.text_input("Name")
    new_password = register_user_form.text_input("Password", type="password")
    new_password_repeat = register_user_form.text_input(
        "Repeat password", type="password"
    )

    if register_user_form.form_submit_button("Register"):
        if (
            len(new_email)
            and len(new_username)
            and len(new_name)
            and len(new_password) > 0
        ):
            if new_username not in [u.username for u in session.query(db.User).all()] and \
                new_email not in [u.email for u in session.query(db.User).all()]:
                if new_password == new_password_repeat:
                    auth._register_credentials(
                        new_username, new_name, new_password, new_email, False
                    )
                    st.session_state["username"] = new_username
                    st.session_state["name"] = new_name
                    st.session_state["authentication_status"] = True
                    return True
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Username or email already exists")
        else:
            st.error("Please fill in all fields")

    session.close()
    return False


def is_logged_in():
    """
    This function checks if the user is logged in.
    If the user is not logged in, the login page is displayed.
    """
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = False

    if not st.session_state["authentication_status"]:
        return False

    return True

