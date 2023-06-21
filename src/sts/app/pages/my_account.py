import streamlit as st
from streamlit_extras.app_logo import add_logo

from sts.utils.streamlit_utils import get_authenticator

add_logo(logo_url="src/sts/img/Style-Transfer_Webshop_Logo.png", height=80)
auth = get_authenticator()
res = auth.login("Login to access the app", location="sidebar")

if not res[1]:
    st.markdown("# Stop")
    st.markdown("Please login to use this feature")
    st.stop()
