import streamlit as st

from sts.app.database import add_users
from sts.utils.streamlit_utils import (
    get_authenticator,
    check_if_logged_in,
    display_register,
)

from streamlit_extras.app_logo import add_logo


def main():
    """
    This is the main function of the app.
    It is called when the app is started.
    """

    st.title("Style Transfer Shop")
    add_logo(logo_url="src/sts/img/Style-Transfer_Webshop_Logo.png", height=80)
    auth = get_authenticator()

    if not check_if_logged_in():
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_res = auth.login("Login to access the app", location="main")
            if login_res[1]:
                st.experimental_rerun()

        with tab2:
            reg_res = display_register(auth)
            if reg_res:
                st.success("You are registered!")
                add_users(auth.credentials)
                st.experimental_rerun()

    else:
        st.success("You are logged in!")
        auth.logout("Logout", location="sidebar")


if __name__ == "__main__":
    main()
