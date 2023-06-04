import streamlit as st

from sts.utils.streamlit_utils import get_authenticator

auth = get_authenticator()
res = auth.login("Login to access the app", location="sidebar")

if not res[1]:
    st.markdown("# Stop")
    st.markdown("Please login to use this feature")
    st.stop()
