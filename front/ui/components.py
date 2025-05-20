import streamlit as st
import asyncio
from typing import Optional
from front.services.mcp_service import MCPService
from front.services.openai_service import OpenAIService
# env 파일 사용
from dotenv import load_dotenv
import os

load_dotenv()

def initialize_chat():
    """
    Initialize chat session.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_messages():
    """
    Display chat messages.
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            display_user_message(message["content"])
        else:
            display_assistant_message(message["content"])

def display_user_message(message: str):
    """
    Display user message.
    """
    with st.chat_message("user"):
        st.write(message)

def display_assistant_message(message: str):
    """
    Display assistant message.
    """
    with st.chat_message("assistant"):
        st.write(message)

def display_streaming_response(response, message_placeholder):
    """
    Display streaming response.
    """
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response

def render_sidebar(mcp_service: MCPService) -> Optional[str]:
    """
    Render sidebar with settings.
    """
    if "mcp_servers" not in st.session_state:
        st.session_state.mcp_servers = {}
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""

    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown("---")

        # OpenAI API Key
        st.markdown("#### 🔑 OpenAI API Key")
        env_openai_api_key = os.getenv("OPEN_AI_API_KEY")
        if env_openai_api_key:
            st.session_state.openai_api_key = env_openai_api_key
        else:
            env_openai_api_key = ""

        openai_api_key = st.text_input(
            "Enter OpenAI API Key",
            value=st.session_state.get("openai_api_key", env_openai_api_key),
            type="password",
            key="openai_api_key_input",
            label_visibility="collapsed"            
        )
        if st.button("Save API Key", use_container_width=True):
            st.session_state.openai_api_key = openai_api_key
            st.success("API key saved.", icon="✅")
        elif st.session_state.get("openai_api_key"):
            st.info("API key is set.", icon="🔒")
        else:
            st.warning("API key is required.", icon="⚠️")

        st.markdown("---")
        st.markdown("#### 🖧 MCP Servers")

        # Server Status
        if mcp_service.has_servers():
            st.success("✅ MCP servers are registered.")
        else:
            st.warning("⚠️ No MCP servers. Using default LLM only.")

        # Add new server
        with st.expander("Add Server", expanded=False):
            new_server_name = st.text_input("Server Name", key="new_server_name", value="test")
            new_server_url = st.text_input("Server URL", key="new_server_url", value="http://127.0.0.1:9000/mcp")
            if st.button("Add Server", use_container_width=True) and new_server_name and new_server_url:
                st.session_state.mcp_servers[new_server_name] = new_server_url
                st.rerun()

        # Display and manage existing servers
        if mcp_service.has_servers():            
            st.markdown("**Registered Servers**")
            for server_name, server_url in st.session_state.get("mcp_servers", {}).items():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{server_name}: {server_url}")
                with col2:
                    if st.button("X", key=f"remove_{server_name}", use_container_width=True):
                        del st.session_state.mcp_servers[server_name]
                        st.rerun()

        # Server selection
        if mcp_service.has_servers():
            async def get_available_servers():
                return await mcp_service.list_available_servers()
            servers = asyncio.run(get_available_servers())
            return st.selectbox(
                "Select MCP Server",
                ["All Servers"] + servers,
                index=0
            )
        return None

def render_chat_interface(
    mcp_service: MCPService,
    openai_service: OpenAIService,
    selected_server: Optional[str]
):
    """
    Render chat interface.
    """
    initialize_chat()
    st.title("MCP Chat Client")
    display_chat_messages()
    
    if prompt := st.chat_input("What would you like to know?"):
        try:
            async def process_with_mcp():
                server_name = None if selected_server == "All Servers" else selected_server
                return await mcp_service.process_prompt(prompt, server_name)
            
            processed_prompt = asyncio.run(process_with_mcp())
            if processed_prompt != prompt:
                st.info("Your input was processed by MCP before sending.")
        except Exception as e:
            st.warning(str(e))
            processed_prompt = prompt
        
        st.session_state.messages.append({"role": "user", "content": processed_prompt})
        display_user_message(processed_prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                response = openai_service.get_chat_response(
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )
                print(f"response: {response}")
                full_response = display_streaming_response(response, message_placeholder)
                
            except Exception as e:
                st.error(str(e))
                full_response = ""
        
        st.session_state.messages.append({"role": "assistant", "content": full_response}) 