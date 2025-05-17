import asyncio
import streamlit as st
from chatbot import Chatbot

async def main():
    if "server_connected" not in st.session_state:
        st.session_state["server_connected"] = False

    if "tools" not in st.session_state:
        st.session_state["tools"] = []

    if "message" not in st.session_state:
        st.session_state["messages"] = []
    
    API_URL = "http://localhost:9001"

    st.set_page_config(page_title="MCP Client", page_icon=":robot_face:")

    st.title("🤖 MCP Client")

    chatbot = Chatbot(API_URL)

    await chatbot.render()


if __name__ == "__main__":
    asyncio.run(main())