import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from models.authentication_models import AuthenticationModel as _AuthenticationModel
from models.authentication_models import LoginError
from models.authentication_validator import Validator


@st.cache_resource
def load_config():
    with open("./models/config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    STREAMLIT_AUTH_KEY = os.getenv("STREAMLIT_AUTH_KEY")
    if STREAMLIT_AUTH_KEY is None:
        raise ValueError("STREAMLIT_AUTH_KEY is not set")

    config["cookie_key"] = STREAMLIT_AUTH_KEY
    return config


def load_authenticator() -> stauth.Authenticate:
    config = load_config()
    if "global_authenticator" not in st.session_state:
        authenticator = stauth.Authenticate(
            credentials=config["credentials"],
            cookie_name=config["cookie_name"],
            cookie_key=config["cookie_key"],
            cookie_expiry_days=config["cookie_expiry_days"],
            validator=Validator(config["mail_whitelist"])
        )

        # Patch the AuthenticationModel to use our custom one
        authenticator.authentication_controller.authentication_model = _AuthenticationModel(
            credentials=config["credentials"],
        )

        st.session_state["global_authenticator"] = authenticator

    return st.session_state["global_authenticator"]


def wipe_cookie(authenticator: stauth.Authenticate):
    ref = authenticator.cookie_controller.cookie_model
    ref.cookie_manager.set(ref.cookie_name, "")


def pre_login() -> bool:
    authenticator = load_authenticator()
    if not st.session_state.get("authentication_status") and not st.session_state.get("username"):
        token = authenticator.cookie_controller.get_cookie()
        if token:
            try:
                authenticator.authentication_controller.login(token=token)
            except LoginError:
                wipe_cookie(authenticator)
    return False
