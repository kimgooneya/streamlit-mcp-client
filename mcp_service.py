from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from mcp import Tool
from typing import Dict, List


class MCPService:
    def __init__(self, openai_service):
        self.clients: Dict[str, Client] = {}
        self.tools: Dict[str, List[Tool]] = {}
        self.openai_service = openai_service
        self.transport = StreamableHttpTransport(url="http://127.0.0.1:9000/mcp")
        
    async def connect(self):
        """MCP 서버에 연결하고 도구 목록을 가져옵니다."""
        if not self.clients:
            client = Client(transport=self.transport)
            async with client:
                await client.ping()
                tools = await client.list_tools()
                self.tools["default"] = tools
            self.clients["default"] = client
            return tools
        return self.tools["default"]
    
    async def call_tool(self, tool_name: str, parameters: dict):
        """MCP 도구를 호출합니다."""
        if "default" not in self.clients:
            await self.connect()
        
        client = self.clients["default"]
        async with client:
            return await client.call_tool(tool_name, parameters)
    
    def get_available_tools(self):
        """사용 가능한 도구 목록을 반환합니다."""
        return self.tools.get("default", [])
        
