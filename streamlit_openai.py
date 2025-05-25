import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os


def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'client' not in st.session_state:
        # .env 파일에서 API 키 로드
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OPENAI_API_KEY not found in .env file")
            return
        st.session_state['client'] = OpenAI(api_key=api_key)


def get_chat_response(messages):
    try:
        response = st.session_state['client'].chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting response from OpenAI: {str(e)}")
        return None


def main():
    st.set_page_config(
        page_title="OpenAI Chat Bot",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("OpenAI Chat Bot 🤖")
    
    # 채팅 메시지 표시
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("Ask me anything"):
        # 사용자 메시지 추가
        st.session_state['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # OpenAI 응답 생성
        with st.spinner("Thinking..."):
            response = get_chat_response(st.session_state['messages'])
            if response:
                st.session_state['messages'].append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.write(response)


if __name__ == "__main__":
    main()
