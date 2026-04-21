from __future__ import annotations

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PATH = Path(__file__).with_name("server.py")


async def main() -> None:
    server_params = StdioServerParameters(
        command="python",
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            resources = await session.list_resources()
            print("\nAvailable resources:")
            for resource in resources.resources:
                print(f"- {resource.uri}: {resource.name}")

            result = await session.call_tool("add", {"a": 20, "b": 22})
            print("\nCall tool `add(20, 22)` result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
