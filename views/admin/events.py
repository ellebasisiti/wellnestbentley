import streamlit as st

from models.rbac import require_admin

require_admin()

st.header("Events")

st.warning("This page is under construction", icon="🚧")
