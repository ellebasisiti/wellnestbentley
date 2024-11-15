import openai
import streamlit as st


@st.cache_resource(show_spinner=False)
def get_openai():
    return openai.OpenAI()
