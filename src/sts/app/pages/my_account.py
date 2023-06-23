import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd

from sts.utils.streamlit_utils import get_authenticator, is_logged_in
from sts.app.database import get_user_information, get_order_information, check_if_order


def display_user_information():
    """
    The user can have a look at the information which they
    are registered with
    """
    user_data = get_user_information(st.session_state["username"])
    print(st.session_state["username"])

    st.write("This is the information about your account")
    st.write("User Information:")
    user_information_table = pd.DataFrame(user_data)
    st.table(user_information_table)


add_logo(logo_url="src/sts/img/Style-Transfer_Webshop_Logo.png", height=80)
auth = get_authenticator()
res = auth.login("Login to access the app", location="sidebar")
def display_order_information():
    """
    The user can have a look at the information of their places orders.
    """
    st.write("These are the orders you have placed:")
    oder_data = get_order_information(st.session_state["username"])
    oder_information_table = pd.DataFrame(oder_data)
    st.table(oder_information_table)


def display_login_possibility():
    """
    Creates the page, that should be shown, when not logged in yet.
    """
    st.warning("Stop! Please login to use this feature")
    auth = get_authenticator()
    res = auth.login("Login to access the app", location="sidebar")


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
            print("is order")
    else:
        display_login_possibility()


if __name__ == "__main__":
    main()
