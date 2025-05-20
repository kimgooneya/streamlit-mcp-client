# Streamlit MCP Client

MCP(Multi-Client Protocol) 서버와 통신하는 Streamlit 기반의 채팅 클라이언트입니다.

## 기능

- OpenAI API를 통한 채팅 기능
- MCP 서버 연동
- 다중 MCP 서버 지원
- 실시간 스트리밍 응답
- 서버 상태 모니터링

## 설치

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/streamlit-mcp-client.git
cd streamlit-mcp-client
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

## 실행

```bash
streamlit run main.py
```

## 사용 방법

1. 사이드바에서 OpenAI API 키를 입력합니다.
2. MCP 서버를 추가합니다 (선택사항).
   - 서버 이름과 URL을 입력하여 추가할 수 있습니다.
   - 기본 서버 URL: http://localhost:8000
3. 채팅 인터페이스에서 메시지를 입력합니다.

## 라이선스

MIT License
