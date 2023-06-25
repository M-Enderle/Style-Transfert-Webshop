import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd
from streamlit_extras.app_logo import add_logo
from sts.utils.streamlit_utils import get_authenticator, is_logged_in
from sts.app.database import get_user_information, get_order_information, check_if_order

add_logo(logo_url="src/sts/img/Style-Transfer_Webshop_Logo.png", height=80)


def display_user_information():
    """
    The user can have a look at the information which they
    are registered with
    """
    user_data = get_user_information(st.session_state["username"])
    if len(user_data) > 0:
        st.write("This is the information about your account")
        st.write("User information:")
        st.text_input("Username", disabled=True, value=user_data["Username"])
        st.text_input("Name", disabled=True, value=user_data["Name"])
        st.text_input("E-Mail", disabled=True, value=user_data["E-mail"])
    else:
        st.session_state["username"] = None
        st.experimental_rerun()


def display_order_information():
    """
    The user can have a look at the information of their places orders.
    """
    order_data = get_order_information(st.session_state["username"])
    if len(order_data) > 0:
        st.write("These are the orders you have placed:")
        order_information_table = pd.DataFrame(order_data)
        st.table(order_information_table)


def display_login_possibility():
    """
    Creates the page, that should be shown, when not logged in yet.
    """
    st.warning(
        "You have to log in to use the features of the Webshop. Please log in."
        "If you do not have an account yet, feel free to register in home."
    )
    auth = get_authenticator()
    auth.login("Login to access the app", location="sidebar")


def main() -> None:
    """
    This handles the checking of the logged in status and
    organizes what should be shown at the moment.
    """
    st.title("My Account")
    if is_logged_in():
        display_user_information()
        if check_if_order(st.session_state["username"]):
            display_order_information()
    else:
        display_login_possibility()


if __name__ == "__main__":
    main()
