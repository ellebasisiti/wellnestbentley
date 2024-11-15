import streamlit as st

from models.auth import load_authenticator
from models.rbac import Roles
from views.profiles.logo import show_logo

authenticator = load_authenticator()

try:
    show_logo()
    (email_of_registered_user,
     username_of_registered_user,
     name_of_registered_user) = authenticator.register_user(
        roles=Roles("user")
    )
    if email_of_registered_user:
        st.success('User registered successfully, please login.')
        st.balloons()

    st.page_link("views/profiles/login.py", label="Already have an account? Login here.")
except Exception as e:
    st.error(e)
