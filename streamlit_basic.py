import streamlit as st


def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []


def main():
    st.set_page_config(
        page_title="Echo Chat Bot",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("Echo Chat Bot 🤖")
    
    # 채팅 메시지 표시
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("Say something"):
        # 사용자 메시지 추가
        st.session_state['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # 봇 응답 (에코)
        response = f"Echo: {prompt}"
        st.session_state['messages'].append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)


if __name__ == "__main__":
    main()
