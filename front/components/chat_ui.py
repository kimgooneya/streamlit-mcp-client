import streamlit as st

def initialize_chat():
    """
    Initialize chat session state
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_messages():
    """
    Display all chat messages
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def display_user_message(message: str):
    """
    Display user message in chat
    """
    with st.chat_message("user"):
        st.markdown(message)

def display_assistant_message(message: str):
    """
    Display assistant message in chat
    """
    with st.chat_message("assistant"):
        st.markdown(message)

def display_streaming_response(response, message_placeholder):
    """
    Display streaming response from assistant
    """
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response 
