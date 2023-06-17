# https://github.com/mkhorasani/Streamlit-Authenticator

import streamlit as st
import streamlit_authenticator as stauth

import sts.app.database as db
from sts.utils.utils import load_user_toml

session = db.session
user_data = load_user_toml()


def get_authenticator() -> stauth.Authenticate:
    """
    Returns a streamlit_authenticator.Authenticate object
    """

    users = session.query(db.User).all()
    credentials: dict = {"usernames": {}}
    for user in users:
        credentials["usernames"][user.username] = {
            "password": user.password_hash,
            "email": user.email,
            "name": user.name,
        }

    return stauth.Authenticate(
        credentials=credentials,
        cookie_name=user_data["stauth"]["cookie_name"],
        key=user_data["stauth"]["cookie_secret_key"],
        cookie_expiry_days=user_data["stauth"]["cookie_expiry_days"],
    )
