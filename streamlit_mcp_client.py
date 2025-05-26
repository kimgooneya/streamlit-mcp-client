import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from fastmcp import Client
import json
from dataclasses import asdict


def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'client' not in st.session_state:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OPENAI_API_KEY not found in .env file")
            return
        st.session_state['client'] = OpenAI(api_key=api_key)
    if 'mcp_server' not in st.session_state:
        st.session_state['mcp_server'] = Client("http://127.0.0.1:9000/mcp", timeout=30.0)


def tool_to_dict(tool):
    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": tool.inputSchema,
        "annotations": tool.annotations
    }


def safe_json_parse(text):
    """Safely parse JSON from text that might contain 'json' prefix or other text."""
    try:
        # Remove any 'json' prefix if it exists
        text = text.strip()
        if text.lower().startswith('json'):
            text = text[4:].strip()
        
        # Remove any markdown code block markers if they exist
        text = text.replace('```json', '').replace('```', '').strip()
        
        return json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {str(e)}")
        st.write("Raw response:", text)
        return None


async def get_mcp_response(prompt):
    try:
        async with st.session_state['mcp_server']:
            # First, get available tools
            tools = await st.session_state['mcp_server'].list_tools()
            
            # Convert tools to JSON-serializable format
            tools_json = [tool_to_dict(tool) for tool in tools]
            
            # Create a prompt for the AI to analyze which tool to use
            analysis_prompt = f"""Given the user's question: "{prompt}"
            Available tools with their details:
            {json.dumps(tools_json, indent=2, ensure_ascii=False)}
            
            Please analyze which tool would be most appropriate and what parameters would be needed.
            Respond in JSON format with:
            {{
                "selected_tool": "tool_name",
                "parameters": {{
                    "param1": "value1",
                    "param2": "value2"
                }},
                "explanation": "why this tool was selected"
            }}"""
            
            # Get AI's analysis
            response = st.session_state['client'].chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.7,
            )
            
            response_text = response.choices[0].message.content
            st.write("AI Response:", response_text)
            
            analysis = safe_json_parse(response_text)
            if not analysis:
                return None
            
            # Execute the selected tool
            result = await st.session_state['mcp_server'].call_tool(
                analysis['selected_tool'],
                analysis['parameters']
            )
            
            return {
                "analysis": analysis,
                "result": result
            }
    except Exception as e:
        st.error(f"Error in MCP communication: {str(e)}")
        return None


def main():
    st.set_page_config(
        page_title="MCP Client with OpenAI Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("MCP Client with OpenAI Chat 🤖")
    
    # Main chat interface
    st.subheader("Chat Interface")
    # Display chat messages
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input for chat
    if prompt := st.chat_input("Ask me anything"):
        st.session_state['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.spinner("Thinking..."):
            response = asyncio.run(get_mcp_response(prompt))
            if response:
                # Display the analysis
                with st.chat_message("assistant"):
                    st.write("Tool Analysis:")
                    st.json(response['analysis'])
                    
                    st.write("Tool Result:")
                    st.json(response['result'])
                


if __name__ == "__main__":
    main() 