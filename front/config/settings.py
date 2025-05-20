import streamlit as st
from typing import Dict

# OpenAI Configuration
def get_openai_api_key() -> str:
    """
    OpenAI API 키를 반환합니다.
    """
    return st.session_state.get("openai_api_key", "")

# MCP Configuration
def get_mcp_servers() -> Dict[str, str]:
    """
    MCP 서버 목록을 반환합니다.
    """
    return st.session_state.get("mcp_servers", {})