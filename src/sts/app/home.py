import streamlit as st
import streamlit_authenticator as stauth
from sts.app.database import User, add_users, create_session
from sqlalchemy.exc import IntegrityError

from sts.utils.streamlit_utils import (
    get_authenticator, 
    is_logged_in,
    display_register
)


def logged_in_home():
    """
    This creates the homepage, which the user can see, when logged in.
    A short description of the WebShop and how it works is included.
    The user can logout if they want to.
    """
    st.write(
        "Welcome to our Style Transfer Webshop!"
        "Create unique and artistic images by combining "
        "the styles of two different pictures."
    )
    st.header("How it Works")
    st.markdown(
        """
        1. Upload an image you want to apply the style to (Content Image).
        2. Upload an image that represents the desired artistic style (Style Image).
        3. Our AI model will apply the style of the Style Image to the Content Image.
        4. You can then select from a range of products to print your AI-generated image on!

        Get started now and unleash your creativity!
    """
    )


def main() -> None:
    """
    This handles the checking of the logged in status and
    organizes what should be shown at the moment.
    """
    st.title("Style Transfer Shop")
    auth = get_authenticator()
    if is_logged_in():
        st.success("You are logged in!")
        logged_in_home()
        auth.logout("Logout", location="sidebar")
    else:
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


if __name__ == "__main__":
    main()
