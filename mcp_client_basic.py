import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

transport = StreamableHttpTransport(url="http://127.0.0.1:9000/mcp")
client = Client(transport)


async def main():
    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")


if __name__ == "__main__":
    asyncio.run(main())