import streamlit as st
import streamlit_authenticator as stauth
from database import session, engine, User
from sqlalchemy.exc import IntegrityError

from sts.utils.streamlit_utils import get_authenticator, is_logged_in

st.title("Style Transfer Shop")
auth = get_authenticator()


def register_user(username, name, email, password):
    """
    This function tries to register a new user. If the users E-Mail
    or username already exists in the database, there will be an Integrity Error
    and the user will see a warning, that he cannot register. Otherwise the user is
    registered in the database.
    :params:
        username: username the user entered
        name: name the user entered
        email: email the user entered
        password: password the user entered
    """
    try:
        user = User(username=username, name=name, email=email)
        print("yippie")
        user.set_plain_password(password)

        session.add(user)
        session.commit()

        st.session_state["name"] = name
        st.session_state["authentication_status"] = True
        st.session_state["username"] = username
        st.session_state["email"] = email
        st.experimental_rerun()
    except IntegrityError:
        session.rollback()
        st.error("Username or email already exists!")
        return


def display_register():
    """
    This page is displayed, when the user clicks on the Register Tab.
    Here the user can enter his personal information and try to register
    in the WebApp.
    """
    st.title("User Registration")

    username = st.text_input("Username")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register now"):
        if username and name and email and password:
            register_user(username, name, email, password)
            st.success("You are succesfully registered. Log In now.")
        else:
            st.error("Please fill in all the fields.")


def display_login():
    """
    This page is displayed, when the user first visits our home-page, or when they click
    on the Login-tab. The user can enter his login information and login to the app. When logged
    in succesfully, it will be saved in the session.
    """
    res = auth.login("Login to access the app")
    st.warning("Not registered yet? Just click on Register.")
    st.markdown(
        """
        test_user:<br>
        name: test<br>
        password: 3PXzAxtU6PSbCohf<br>
        email: test@test.com<br>
        """,
        unsafe_allow_html=True,
    )


def display_buttons():
    """
    This creates the buttons to switch in between the Register and the
    Login Layout.
    """
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        display_login()

    with tab2:
        display_register()


def logged_in_home():
    """
    This creates the homepage, which the user can see, when logged in.
    A short description of the WebShop and how it works is included.
    The user can logout if they want to.
    """
    auth.logout("Logout")
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
    if is_logged_in():
        logged_in_home()
    else:
        display_buttons()


if __name__ == "__main__":
    main()
