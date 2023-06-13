import streamlit as st
import streamlit_authenticator as stauth
from database import session, engine, User
from sqlalchemy.exc import IntegrityError

from sts.utils.streamlit_utils import get_authenticator

st.title("Style Transfer Shop")
auth = get_authenticator()

def register_user(username, name, email, password):
    try:
        user = User(username=username, name=name, email=email)
        print("yippie")
        user.set_plain_password(password)

        session.add(user)
        session.commit()

        st.session_state['name'] = name 
        st.session_state['authentication_status'] = True
        st.session_state['username'] = username
        st.experimental_rerun()
    except IntegrityError:
        session.rollback()
        st.error("Username or email already exists!")
        return



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


def display_login(after_register=False):
    if after_register:
        st.success("User registered successfully! Now log in!")

    
    res = auth.login("Login to access the app")

    if res[1]:
        st.write("You are succesfully logged in!")
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


def logged_in_home():
    st.title("Style Transfer Webshop")
    st.write("Welcome to our Style Transfer Webshop! Create unique and artistic images by combining the styles of two different pictures.")
    auth.logout("Logout")
    st.header("How it Works")
    st.markdown("""
        1. Upload an image you want to apply the style to (Content Image).
        2. Upload an image that represents the desired artistic style (Style Image).
        3. Our AI model will apply the style of the Style Image to the Content Image.
        4. You can then select from a range of products to print your AI-generated image on!

        Get started now and unleash your creativity!
    """)
        


def main() -> None:
    
    #if TODO moritzmethode:
    #   logged_in_home()
    #else
        display_buttons()

    


if __name__ == "__main__":
    main()
