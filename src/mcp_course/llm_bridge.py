from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SERVER_PATH = Path(__file__).with_name("server.py")
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://10.0.0.63:1234/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
MODEL = os.getenv("OPENAI_MODEL", "qwen/qwen3.6-35b-a3b")


def to_openai_tools(mcp_tools) -> list[dict]:
    out = []
    for tool in mcp_tools:
        schema = tool.inputSchema if getattr(tool, "inputSchema", None) else {"type": "object", "properties": {}}
        out.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": schema,
                },
            }
        )
    return out


async def main() -> None:
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    server_params = StdioServerParameters(command="python", args=[str(SERVER_PATH)])

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_response = await session.list_tools()
            openai_tools = to_openai_tools(tools_response.tools)

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use tools when useful, especially for exact facts and calculations.",
                },
                {
                    "role": "user",
                    "content": "今天是 2026-04-20。请调用工具，告诉我 2026-04-20 到 2026-05-01 相差几天，并顺便给我一句关于学习 MCP 的建议。",
                },
            ]

            first = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
            )

            assistant_message = first.choices[0].message
            messages.append(assistant_message.model_dump())

            for tool_call in assistant_message.tool_calls or []:
                arguments = json.loads(tool_call.function.arguments)
                result = await session.call_tool(tool_call.function.name, arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": json.dumps(result.model_dump(), ensure_ascii=False),
                    }
                )

            final = client.chat.completions.create(model=MODEL, messages=messages)
            print(final.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())
