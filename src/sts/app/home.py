import streamlit as st
import streamlit_authenticator as stauth
from database import session, engine, User
from sqlalchemy.exc import IntegrityError

from sts.utils.streamlit_utils import get_authenticator

st.title("Style Transfer Shop")
auth = get_authenticator()
res = auth.login("Login to access the app", location="sidebar")

def register_user(username, name, email, password):
    try:
        user = User(username=username, name=name, email=email)
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
    st.title("User Login")


if not res[1]:
    st.markdown(
        """
        test_user:<br>
        name: test<br>
        password: 3PXzAxtU6PSbCohf<br>
        email: test@test.com<br>
    """,
        unsafe_allow_html=True,
    )
    

else:
    auth.logout("Logout")


def main() -> None:
    
    current_page = st.session_state.get("current_page")
    if current_page == display_register:
        display_register()
    elif current_page == display_login:
        display_login()
        
    if st.button('Login'):
        display_login()
        st.session_state["current_page"] = display_login

    elif st.button('Register'):
        display_register()  
        st.session_state["current_page"] = display_login


if __name__ == "__main__":
    main()
