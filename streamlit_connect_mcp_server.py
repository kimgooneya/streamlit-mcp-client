import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from mcp_service import MCPService
import json


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
    if 'mcp_service' not in st.session_state:
        st.session_state['mcp_service'] = MCPService(st.session_state['client'])


def get_chat_response(messages):
    try:
        response = st.session_state['client'].chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting response from OpenAI: {str(e)}")
        return None


async def connect_mcp():
    try:
        tools = await st.session_state['mcp_service'].connect()
        return tools
    except Exception as e:
        st.error(f"Error connecting to MCP service: {str(e)}")
        return None


async def call_mcp_tool(tool_name, parameters):
    try:
        result = await st.session_state['mcp_service'].call_tool(tool_name, parameters)
        return result
    except Exception as e:
        st.error(f"Error calling MCP tool: {str(e)}")
        return None


def main():
    st.set_page_config(
        page_title="MCP Client with OpenAI Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("MCP Client with OpenAI Chat 🤖")
    
    # MCP Tools in sidebar
    with st.sidebar:
        st.subheader("MCP Tools")
        
        # Connect to MCP service
        if st.button("Connect to MCP Service"):
            with st.spinner("Connecting to MCP service..."):
                tools = asyncio.run(connect_mcp())
                if tools:
                    st.success("Connected to MCP service!")
                    st.session_state['available_tools'] = tools
        
        # Display available tools
        if 'available_tools' in st.session_state:
            st.write("Available Tools:")
            for tool in st.session_state['available_tools']:
                with st.expander(f"Tool: {tool.name}"):
                    st.write(f"Description: {tool.description}")
                    st.write("Parameters:")
                    for key, value in tool.inputSchema['properties'].items():
                        st.write(f"- {key}: {value}")
                    
    
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
            # First, get AI's analysis of which tool to use
            tools_info = []
            for tool in st.session_state.get('available_tools', []):
                tool_info = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema['properties']
                }
                tools_info.append(tool_info)
            
            analysis_prompt = f"""Given the user's question: "{prompt}"
            Available tools with their details:
            {json.dumps(tools_info, indent=2)}
            
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
            
            analysis_messages = st.session_state['messages'] + [{"role": "user", "content": analysis_prompt}]
            analysis_response = get_chat_response(analysis_messages)
            
            if analysis_response:
                try:
                    analysis = json.loads(analysis_response)
                    
                    # Display the analysis
                    with st.chat_message("assistant"):
                        st.write("Tool Analysis:")
                        st.json(analysis)
                    
                except json.JSONDecodeError:
                    st.error("Failed to parse AI's analysis response")
                    st.write(analysis_response)


if __name__ == "__main__":
    main() 