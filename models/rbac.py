import streamlit as st

ROLES = ['user', 'editor', 'admin']


class Roles(list):
    def __init__(self, *args):
        """
        Check if the roles are valid
        """
        for role in args:
            if role not in ROLES:
                raise ValueError(f"Invalid role: {role}")
        super().__init__(role for role in args)


def _is_logged_in() -> bool:
    return "roles" in st.session_state and st.session_state["roles"]


def _is_admin() -> bool:
    return _is_logged_in() and "admin" in st.session_state["roles"]


def _is_editor() -> bool:
    return _is_logged_in() and "editor" in st.session_state["roles"]


def require_admin():
    if _is_logged_in() and _is_admin():
        return

    st.error("Sorry, only the admin can access this page")
    st.rerun()


def require_editor():
    if _is_logged_in() and _is_editor():
        return

    st.error("Sorry, only the editor can access this page")
    st.rerun()


def require_logged_in():
    if not _is_logged_in():
        st.error("Sorry, please login to continue")
        st.rerun()
