import streamlit as st
from front.services.mcp_service import MCPService
from front.services.openai_service import OpenAIService
from front.ui.components import render_sidebar, render_chat_interface
from front.config.settings import get_openai_api_key

def main():
    st.set_page_config(
        page_title="MCP Chat Client",
        page_icon="🤖",
        layout="wide"
    )
    
    # 서비스 초기화
    openai_service = OpenAIService()
    mcp_service = MCPService(openai_service)
    
    # 사이드바 렌더링
    selected_server = render_sidebar(mcp_service)
    
    # 채팅 인터페이스 렌더링
    render_chat_interface(mcp_service, openai_service, selected_server)

if __name__ == "__main__":
    main()

