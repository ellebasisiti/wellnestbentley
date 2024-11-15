import streamlit as st
from streamlit_authenticator.utilities import LoginError

from models.auth import load_authenticator
from views.profiles.logo import show_logo

authenticator = load_authenticator()

try:
    show_logo()
    authenticator.login()
    st.page_link("views/profiles/register.py", label="Don't have an account? Register here.")
except LoginError as e:
    st.error(e)

if "authentication_status" in st.session_state:
    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
    elif "authentication_need_credentials" in st.session_state and st.session_state["authentication_need_credentials"]:
        st.warning("Please enter username and password")
