import openai
from dotenv import load_dotenv
import os

class OpenAIService:
    def __init__(self):
        self._update_api_key()
    
    def _update_api_key(self):
        """
        OpenAI API 키를 업데이트합니다.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
    
    def get_chat_response(self, messages: list, stream: bool = True):
        """
        Get response from OpenAI chat completion
        """
        try:
            # API 키가 변경되었을 수 있으므로 업데이트
            self._update_api_key()
            
            if not openai.api_key:
                raise Exception("OpenAI API key is not set. Please set it in the sidebar.")
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}") 