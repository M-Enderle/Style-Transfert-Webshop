import streamlit as st
import streamlit_authenticator as stauth
from database import session, engine, User
from sqlalchemy.exc import IntegrityError

from sts.utils.streamlit_utils import get_authenticator

st.title("Style Transfer Shop")


def register_user(username, name, email, password):
    try:
        user = User(username=username, name=name, email=email)
        print("yippie")
        user.set_plain_password(password)

        session.add(user)
        session.commit()
        st.success("User registered successfully!")
    except IntegrityError:
        session.rollback()
        st.error("Username or email already exists!")


def display_register():
    st.title("User Registration")

    username = st.text_input("Username")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register now"):
        if username and name and email and password:
            register_user(username, name, email, password)
        else:
            st.error("Please fill in all the fields.")


def display_login():
    auth = get_authenticator()
    res = auth.login("Login to access the app")

    if res[1]:
        st.write("You are succesfully logged in!")
        auth.logout("Logout")
    else:
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
    # if not res[1]: TODO amelie use function of Moritz
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        display_login()

    with tab2:
        display_register()
        


def main() -> None:
    

    display_buttons()


    # current_page = st.session_state.get("current_page")
    # if current_page == display_register:
    #    display_register()
    # elif current_page == display_login:
    #    display_login()

    # if "display_register" not in st.session_state:
    #    st.session_state["display_register"] = None

    # if "diplay_login" not in st.session_state:
    #    st.session_state["display_login"] = None

    # if current_page == display_register:
    #    display_buttons()
    #    display_register()
    # if current_page == display_login:
    #    display_buttons()
    #    display_login()


if __name__ == "__main__":
    main()
