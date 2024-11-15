import streamlit as st


def show_logo():
    st.markdown('<img src="app/static/logo.png" class="login-logo"/>', unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .login-logo {
            max-height: 25vh;
            width: auto;
            display: block;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
