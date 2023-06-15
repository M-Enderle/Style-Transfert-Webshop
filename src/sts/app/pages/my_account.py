import streamlit as st
import pandas as pd

from sts.utils.streamlit_utils import get_authenticator

auth = get_authenticator()


def display_my_account():
    """
    Creates the My Account page the user sees, when logged in.
    """
    st.title("My Account")
    auth.logout("Logout")

    tab1, tab2 = st.tabs(["Your information", "Change your information"])

    with tab1:
        display_user_information()

    with tab2:
        display_changeable_information()


def display_user_information():
    """
    The user can have a look at the information which they
    are registered with
    """
    user_information = [{"Username": st.session_state["username"],
                        "Name": st.session_state["name"]
                        #TODO just shows <NA>
                        #TODO key does not exist "Email": st.session_state["email"]
                        }
    ]
    st.write("This is the information about your account")
    st.write("User Information:")
    user_information_table = pd.DataFrame(user_information)
    st.table(user_information_table)




def display_changeable_information():
    """
    If wanting to change something in their user information.
    The user can do this here.
    """


def display_login_possibility():
    """
    Creates the page, that should be shown, when not logged in yet.
    """
    st.markdown("# Stop")
    st.markdown("Please login to use this feature")
    st.stop()
    res = auth.login("Login to access the app", location="sidebar")


def main() -> None:
    """
    This handles the checking of the logged in status and
    organizes what should be shown at the moment.
    """
    # if is_logged_in():
    #    display_my_account()
    # else:
    #    display_login_possibility()

    display_my_account()


if __name__ == "__main__":
    main()
