import streamlit as st
from mcp_service import MCPService
from openai_service import OpenAIService
import asyncio


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mcp_service" not in st.session_state:
        st.session_state.mcp_service = None
    if "openai_service" not in st.session_state:
        st.session_state.openai_service = None
    if "is_connected" not in st.session_state:
        st.session_state.is_connected = False


async def initialize_services():
    try:
        openai_service = OpenAIService()
        mcp_service = MCPService(openai_service)
        await mcp_service.connect()
        st.session_state.openai_service = openai_service
        st.session_state.mcp_service = mcp_service
        st.session_state.is_connected = True
        return True
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        return False


async def process_message(prompt: str):
    try:
        response = await st.session_state.mcp_service.call_tool("greet", {"name": "User"})
        return response
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    st.set_page_config(
        page_title="MCP Chat Client",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session_state()
    
    # 사이드바 설정
    with st.sidebar:
        st.header("Settings")
        
        # OpenAI API 키 설정
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            if not st.session_state.openai_service:
                st.session_state.openai_service = OpenAIService()
            st.session_state.openai_service._update_api_key()
        
        # 연결 상태 표시
        if st.session_state.is_connected:
            st.success("✅ Connected to MCP Server")
        else:
            st.warning("⚠️ Not connected to MCP Server")
        
        # 연결 버튼
        if st.button("Connect to MCP Server", disabled=st.session_state.is_connected):
            with st.spinner("Connecting to MCP Server..."):
                success = asyncio.run(initialize_services())
                if success:
                    st.success("Successfully connected to MCP Server!")
                    st.rerun()
    
    # 메인 채팅 인터페이스
    st.title("MCP Chat Client 🤖")
    
    # 연결되지 않은 경우 안내 메시지 표시
    if not st.session_state.is_connected:
        st.info("Please connect to MCP Server using the sidebar button to start chatting.")
        return
    
    # 채팅 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("What would you like to do?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # MCP 도구 호출
        response = asyncio.run(process_message(prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)


if __name__ == "__main__":
    main()

