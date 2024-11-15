import streamlit as st

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@100..900&family=Noto+Serif:ital,wght@0,100..900;1,100..900&display=swap');

html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, div, input, textarea, a {
    font-family: 'Lexend Deca', serif !important;
}
</style>
"""


def set_font():
    st.html(css)
