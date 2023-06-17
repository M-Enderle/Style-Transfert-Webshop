import streamlit as st
import streamlit_authenticator as stauth

from sts.app.database import User, add_users, session
from sts.utils.streamlit_utils import get_authenticator

st.title("Style Transfer Shop")
auth = get_authenticator()

tab1, tab2 = st.tabs(["Login", "Register"])
with tab1:
    login_res = auth.login("Login to access the app", location="main")

with tab2:
    reg_res = auth.register_user(
        "Register to access the app", location="main", preauthorization=False
    )
    if reg_res:
        add_users(auth.credentials)

if not login_res[1]:
    st.stop()

else:
    auth.logout("Logout")
