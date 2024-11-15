import streamlit as st

from models.auth import load_authenticator, wipe_cookie

@st.dialog("Logout")
def _logout_menu():
    authenticator = load_authenticator()
    st.warning("Want to log out this session?", icon=":material/warning:")
    if st.button("Yes", icon=":material/check:"):
        wipe_cookie(authenticator)
        authenticator.logout(location="unrendered")

def logout_menu():
    left, right = st.sidebar.columns([1, 1])
    left.markdown("### **WellNest**")
    if right.button("Log out", icon=":material/logout:"):
        _logout_menu()
