import streamlit as st
import streamlit_authenticator as stauth

from sts.utils.streamlit_utils import get_authenticator

st.title("Style Transfer Shop")
auth = get_authenticator()
res = auth.login("Login to access the app", location="sidebar")

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
    st.stop()

else:
    auth.logout("Logout")
