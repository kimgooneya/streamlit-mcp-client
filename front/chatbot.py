import streamlit as st
import httpx
from typing import Dict, Any

class Chatbot:
    def __init__(self, api_url:str):
        self.api_url = api_url
        self.message = st.session_state["messages"]

    def render(self):
        st.title("MCP Client")

        with sidebar:
            st.subheader("Settings")
            st.write("API: URL: ", self.api_url)