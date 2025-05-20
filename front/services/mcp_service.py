from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from mcp import Tool
from front.config.settings import get_mcp_servers
from typing import Dict, Optional, Tuple, Any, List
import asyncio

class MCPService:
    def __init__(self, openai_service):
        self.clients: Dict[str, Client] = {}
        self.tools: Dict[str, List[Tool]] = {}
        self.openai_service = openai_service
        self._initialize_clients()
    
    def _initialize_clients(self):
        """
        Initialize clients for each MCP server and load their tools.
        """
        print(f"Initializing clients - mcp servers: {len(get_mcp_servers().items())}")
        self.clients.clear()
        self.tools.clear()
        for server_name, server_url in get_mcp_servers().items():
            try:
                print(f"Initializing client for {server_name} at {server_url}")
                transport = StreamableHttpTransport(url=server_url)
                self.clients[server_name] = Client(transport)
                # 비동기 초기화를 동기적으로 실행
                try:
                    asyncio.run(self.get_tools(server_name))
                except Exception as e:
                    print(f"Failed to initialize tools for {server_name}: {str(e)}")
                    # 클라이언트 초기화 실패 시 해당 서버 제거
                    del self.clients[server_name]
            except Exception as e:
                print(f"Failed to initialize client for {server_name}: {str(e)}")

    async def get_tools(self, server_name: str) -> List[Tool]:
        """
        Get and store tools for a specific server.
        """
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")
            
        if server_name not in self.tools:
            try:
                client = self.get_client(server_name)
                async with client:
                    tools = await client.list_tools()
                    self.tools[server_name] = tools
                    print(f"Loaded {len(tools)} tools from {server_name}")
            except Exception as e:
                print(f"Error loading tools from {server_name}: {str(e)}")
                self.tools[server_name] = []
        return self.tools[server_name]

    async def select_tool(self, server_name: str, prompt: str) -> Tuple[Optional[str], Optional[dict]]:
        """
        Select appropriate tool and parameters using OpenAI.
        """
        tools = await self.get_tools(server_name)
        if not tools:
            return None, None

        tools_description = "\n".join([
            f"- {tool.name}: {tool.description}\n  Parameters: {', '.join([f'{param.name} ({param.type})' for param in tool.parameters])}"
            for tool in tools
        ])
        
        tool_selection_prompt = f"""
        User's question: {prompt}
        Available tools:
        {tools_description}
        
        Please select the most appropriate tool to handle the user's question.
        Response format:
        Tool Name: [selected tool name]
        Parameters: [JSON format parameter values]
        
        Example:
        Tool Name: greet
        Parameters: {{"name": "John"}}
        
        If no appropriate tool is found, return 'none'.
        """
        
        response = self.openai_service.get_chat_response(
            messages=[{"role": "user", "content": tool_selection_prompt}]
        )
        response_text = response.choices[0].message.content.strip()
        
        if response_text == "none":
            return None, None
            
        try:
            lines = response_text.split('\n')
            selected_tool = None
            tool_params = {}
            
            for line in lines:
                if line.startswith('Tool Name:'):
                    selected_tool = line.replace('Tool Name:', '').strip()
                elif line.startswith('Parameters:'):
                    params_str = line.replace('Parameters:', '').strip()
                    tool_params = eval(params_str)
            
            return selected_tool, tool_params
        except Exception as e:
            print(f"Error parsing tool selection: {str(e)}")
            return None, None

    async def process_prompt(self, prompt: str, server_name: Optional[str] = None) -> str:
        """
        Process the prompt using MCP servers.
        """
        if not self.has_servers():
            return prompt
            
        if server_name:
            if server_name not in self.clients:
                raise ValueError(f"Unknown server: {server_name}")
            return await self._process_with_server(server_name, prompt)
        
        results = []
        for name in self.clients.keys():
            try:
                result = await self._process_with_server(name, prompt)
                results.append(result)
            except Exception as e:
                print(f"Error processing with server {name}: {str(e)}")
        
        return " | ".join(results) if results else prompt

    async def _process_with_server(self, server_name: str, prompt: str) -> str:
        """
        Process the prompt with a specific server.
        """
        async with self.clients[server_name]:
            try:
                selected_tool, tool_params = await self.select_tool(server_name, prompt)
                
                if not selected_tool or not tool_params:
                    return prompt
                
                result = await self.clients[server_name].call_tool(selected_tool, tool_params)
                if result and len(result) > 0:
                    return result[0].text
                return prompt
                
            except Exception as e:
                raise Exception(f"MCP processing failed for server {server_name}: {str(e)}")

    def has_servers(self) -> bool:
        """
        Check if there are any registered MCP servers.
        """
        return len(self.clients) > 0

    def get_client(self, server_name: str) -> Client:
        """
        Get the client for a specific server.
        """
        if server_name not in self.clients:
            raise ValueError(f"Unknown server: {server_name}")
        return self.clients[server_name]

    async def list_available_servers(self) -> list[str]:
        """
        Get list of available MCP servers.
        """
        return list(self.clients.keys())

    async def check_server_health(self, server_name: str) -> bool:
        """
        Check health of a specific server.
        """
        if server_name not in self.clients:
            return False
        
        try:
            async with self.clients[server_name]:
                await self.clients[server_name].ping()
                return True
        except Exception:
            return False 
        