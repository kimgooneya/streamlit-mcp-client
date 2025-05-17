from typing import Optional
from contextlib import AsyncExitStack
import traceback

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import datetime
from utils import logger

import json
import os

from openai import OpenAI



class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session:Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.tools = []
        self.messages = []
        self.logger = logger
    
    # connect to the MCP server
    async def connect_to_server(self, server_script_path: str):
        try:
            is_python = server_script_path.endswith(".py")
            is_js = server_script_path.endswith(".js")
            if not (is_python or is_js):
                raise ValueError("Invalid server script path. Must be a Python or JavaScript file.")
            
            command = "python" if is_python else "node"
            server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],
                env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize() 
            self.logger.info("Connected to MCP server")

            mcp_tools = await self.get_mcp_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,                    
                }
                for tool in mcp_tools
            ]

            self.logger.info(f"Available tools: {self.tools}")

        except Exception as e:
            self.logger.error(f"Error connecting to MCP server: {e}")
            traceback.print_exc()
            raise

    # call a mcp tool

    # get mcp tool list
    async def get_mcp_tools(self):
        try:
            tools = await self.session.list_tools()
            return tools;
        except Exception as e:
            self.logger.error(f"Error getting MCP tools: {e}")
            raise

    # proccess query
    async def process_query(self, query: str):
        try:
            self.logger.info(f"Processing query: {query}")
            user_message = { "role": "user", "content": query }
            self.messages = [user_message]

            while True:
                response = await self.call_llm()
                
                # the response is a text message
                if response.content[0].type == "text" and len(response.content) == 1:
                    assistant_message = {
                        "role": "assistant",
                        "content": response.content[0].text
                    }
                    self.messages.append(assistant_message)
                    break

                # the response is a tool call
                assistant_message = {
                    "role": "assistant",
                    "content": response.to_dict()["content"],                    
                }
                self.messages.append(assistant_message)

                for content in response.content:
                    if content.type == "text":
                        self.messages.append(
                            {
                                "role": "assistant",
                                "content": content.text
                            }
                        )
                    if content.type == "tool_call":
                        tool_name = content.name
                        tool_args = content.input
                        tool_use_id = content.id

                        self.logger.info(f"Tool call: {tool_name} with args: {tool_args} and id: {tool_use_id}")

                        try:
                            result = await self.session.call_tool(tool_name, tool_args)
                            self.logger.info(f"Tool call result: {result[:100]}...")
                            self.messages.append({
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "tool_result",
                                            "tool_use_id": tool_use_id,
                                            "content": result.content,
                                        }
                                    ]
                                }
                            )

                        except Exception as e:
                            self.logger.error(f"Error calling tool {tool_name}: {e}")
                            raise

            return self.messages

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise

    # call llm
    async def call_llm(self):
        try:
            self.logger.info("Calling LLM")
            response = await self.llm.messages.create(
                model="gpt-4o-mini",
                instructions="You are agent for MCP Server. You can use the tools provided to you to answer the user's question. You can also use the tools to get more information about the user's question.",
                messages=self.messages,
                tools=self.tools,
            )
            
        
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            raise

    # clean up
    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
            self.logger.info("MCP client cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up MCP client: {e}")
            traceback.print_exc()
            raise

    ## extra

    # log conversation

