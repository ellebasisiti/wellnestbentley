import os
import sys
import streamlit as st

st.set_page_config(
    page_title="WellNest - Mood Calendar with Intelligence & Privacy",
    page_icon="🗓️",
)

from views.font import set_font
from models.auth import pre_login
from models.rbac import _is_logged_in
from models.database import init_database_connection
from views.profiles.logout import logout_menu
from streamlit_theme import st_theme

def exception_handler(e):
    import streamlit as st
    st.error(f"An error occurred with `{type(e).__name__}`, please try again later.", icon="🚨")


@st.fragment()
def init_app():
    APP_DEBUG = os.getenv("APP_DEBUG") == "true"
    if APP_DEBUG:
        st.set_option("client.toolbarMode", "developer")
    else:
        error_util = sys.modules['streamlit.error_util']
        error_util.handle_uncaught_app_exception.__code__ = exception_handler.__code__

    set_font()
    st_theme(adjust=False)

    if not init_database_connection():
        st.error("Failed to connect to database")
        st.stop()

    pages = {}

    pages["login"] = st.Page(
        "views/profiles/login.py", title="Log in", icon=":material/login:", url_path="/login"
    )

    pages["register"] = st.Page(
        "views/profiles/register.py",
        title="Register",
        icon=":material/person_add:",
        url_path="/register",
    )
    pages["profile"] = st.Page(
        "views/profiles/me.py", title="Profile", icon=":material/person:", url_path="/profile"
    )
    pages["calendar"] = st.Page(
        "views/calendar.py",
        title="Calendar",
        icon=":material/date_range:",
        url_path="/calendar",
    )
    pages["summary"] = st.Page(
        "views/summary.py",
        title="Summary",
        icon=":material/insights:",
        url_path="/summary",
    )
    pages["admin_overview"] = st.Page(
        "views/admin/overview.py", title="Overview", icon=":material/settings:", url_path="/admin"
    )
    pages["admin_users"] = st.Page(
        "views/admin/users.py", title="Users", icon=":material/person:", url_path="/admin-users"
    )
    pages["admin_events"] = st.Page(
        "views/admin/events.py", title="Events", icon=":material/event:", url_path="/admin-events"
    )
    pages["admin_resources"] = st.Page(
        "views/admin/resources.py", title="Resources", icon=":material/policy:", url_path="/admin-resources"
    )

    return pages


@st.fragment()
def init_navigation(pages):
    if "username" in st.session_state and st.session_state["username"]:
        navigations = {
            "": [pages["calendar"], pages["summary"], pages["profile"]],
        }
        if "roles" in st.session_state and st.session_state["roles"]:
            if "admin" in st.session_state["roles"]:
                navigations["Admin"] = [pages["admin_overview"], pages["admin_users"], pages["admin_events"],
                                        pages["admin_resources"]]

        pg = st.navigation(navigations, position="sidebar")
    else:
        pg = st.navigation([pages["login"], pages["register"]], position="hidden")

    return pg


pages = init_app()
pre_login()
pg = init_navigation(pages)
if _is_logged_in():
    logout_menu()

pg.run()
