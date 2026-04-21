from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
KERNEL = {
    "kernelspec": {"display_name": "Python (mcp)", "language": "python", "name": "mcp"},
    "language_info": {"name": "python", "version": "3.11"},
}


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


def write_notebook(name: str, cells: list) -> None:
    nb = nbf.v4.new_notebook(cells=cells, metadata=KERNEL)
    nbf.write(nb, ROOT / name)


write_notebook(
    "mcp_01_what_is_mcp.ipynb",
    [
        md(
            """
            # MCP 第 01 课：什么是 MCP，为什么 Agent 世界需要它

            这套课延续前面 agent 课程的风格：**先不用大框架，先把协议和心智模型搞清楚**。

            先回答一个最关键的问题：

            > 为什么已经有 function calling / API / 插件了，还要再来一个 MCP？

            一句话版：

            **MCP 是让“LLM 应用”和“外部能力”之间说同一种语言的标准协议。**
            """
        ),
        md(
            """
            ## 一个具体类比

            没有 MCP 时，常见情况是：

            - 每个 AI 应用都要单独适配每个工具
            - 每个工具都要单独适配每个 AI 应用

            这会形成一个非常痛苦的 `N x M` 集成矩阵。

            有了 MCP 以后：

            - 工具提供方实现一次 MCP server
            - AI 应用实现一次 MCP client
            - 两边就能按标准接起来

            这和 Web 世界里“浏览器说 HTTP，网站也说 HTTP”很像。
            """
        ),
        md(
            """
            ## MCP 不是什么

            MCP **不是模型本身**。

            它也 **不是某个特定厂商的 API**。

            它更像是一套协议层，定义了：

            - server 如何暴露能力
            - client 如何发现能力
            - 双方如何请求、响应、报错、初始化
            """
        ),
        md(
            """
            ## MCP 的三大核心原语

            先记住这三个词，后面会反复出现：

            - `tools`：让模型“做事”
            - `resources`：让模型“读东西”
            - `prompts`：给模型“现成的交互模板”

            再加一个常常被忽略但非常重要的概念：

            - `transport`：消息是通过什么通道传输的，比如 `stdio`、SSE、Streamable HTTP
            """
        ),
        code(
            """
            concepts = {
                "tools": "像函数调用，适合执行动作或查询",
                "resources": "像可读取的数据源，适合把内容加载进上下文",
                "prompts": "像参数化模板，适合复用一段交互模式",
                "transport": "client 和 server 怎么传消息",
            }

            concepts
            """
        ),
        md(
            """
            ## 一个最小世界图

            你可以把 MCP 想成这样：

            ```text
            User -> LLM App (MCP client) -> MCP server -> Tool / File / DB / API
            ```

            这里的关键点不是“LLM 直接干活”，而是：

            **LLM 应用通过 MCP client 去发现和调用 server 暴露出来的能力。**
            """
        ),
        md(
            """
            ## 这门课里的实践路线

            我们不会一开始就讲完整规范细节，而是走一条更工程化的路线：

            1. 先建立 MCP 的整体图景
            2. 再拆开看 tools / resources / prompts
            3. 再从 client 视角理解“初始化、列能力、调用能力”
            4. 最后自己写一个 server，并让本地 LLM 接进来
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **MCP 的价值不在“多了个新概念”，而在“少了很多重复集成工作”。**
            2. **把 tools / resources / prompts 区分清楚，比死记协议字段更重要。**
            3. **学 MCP 最好的方式不是背文档，而是自己写一个 client，再写一个 server。**
            """
        ),
    ],
)

write_notebook(
    "mcp_02_mcp_primitives.ipynb",
    [
        md(
            """
            # MCP 第 02 课：核心原语总览，tools / resources / prompts 到底怎么分

            这一课只做一件事：

            > 把 MCP server 里最重要的三类能力彻底分清楚。
            """
        ),
        md(
            """
            ## 1. Tools：让外部世界“执行动作”

            `tool` 最像我们熟悉的函数调用。

            典型例子：

            - 计算一个值
            - 调某个外部 API
            - 写数据库
            - 执行某个有副作用或确定返回值的动作
            """
        ),
        code(
            """
            def add(a: int, b: int) -> int:
                return a + b

            add(2, 3)
            """
        ),
        md(
            """
            ## 2. Resources：让模型“读取上下文”

            `resource` 更像“可读取的内容入口”。

            它常常适合这类场景：

            - 读取一段文档
            - 读取某个文件
            - 读取系统状态
            - 读取某类结构化数据

            如果你把它类比成 Web 世界，它更接近“GET 一个内容”。
            """
        ),
        code(
            """
            COURSE_OUTLINE = '''
            1. 什么是 MCP
            2. MCP primitives
            3. MCP client
            4. MCP server
            '''.strip()

            COURSE_OUTLINE
            """
        ),
        md(
            """
            ## 3. Prompts：复用一段交互模板

            `prompt` 常常是最容易被忽视的一类能力。

            它不是直接执行动作，而是返回一段可复用的提示模板，方便 client 或上层应用直接调用。
            """
        ),
        code(
            """
            def explain_mcp_prompt(topic: str, audience: str = "beginner") -> str:
                return (
                    f"请用中文向 {audience} 解释 {topic}，"
                    f"要求包含一个类比、一个例子、一个常见误区。"
                )

            explain_mcp_prompt("MCP 中的 tool 和 resource 的区别")
            """
        ),
        md(
            """
            ## 4. Transport：消息如何传

            你可以把 transport 理解成“协议跑在哪条线里”。

            常见有：

            - `stdio`：最适合本地进程对接，简单直接
            - `SSE`：早期很多 MCP HTTP 方案会用到
            - `Streamable HTTP`：更适合现代 HTTP 场景

            在这套课里，我们先用 `stdio`，因为它最容易理解，也最适合本地开发。
            """
        ),
        md(
            """
            ## 一个判断口诀

            当你在设计 server 时，可以先问自己：

            - 我是想让模型**做事**吗？用 `tool`
            - 我是想让模型**读内容**吗？用 `resource`
            - 我是想让模型**拿到一段复用模板**吗？用 `prompt`
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **设计 MCP server 的关键不是“能不能暴露功能”，而是“暴露成哪种原语最合理”。**
            2. **`tool` 往往最显眼，但很多知识型内容其实更适合 `resource`。**
            3. **`prompt` 不是锦上添花，它能把常用工作流变成标准入口。**
            """
        ),
    ],
)

write_notebook(
    "mcp_03_mcp_client.ipynb",
    [
        md(
            """
            # MCP 第 03 课：站在 Client 视角理解协议流

            学 MCP 最容易迷糊的一点，是一上来就看 server 装饰器，结果不知道 client 到底在干什么。

            所以这节课我们反过来：

            > 先从 client 视角看 MCP。
            """
        ),
        md(
            """
            ## 一个最重要的心智模型

            MCP client 的工作，概括起来就四步：

            1. 连接 server
            2. 初始化协议会话
            3. 列出 server 有哪些能力
            4. 调用某个能力

            真正跑起来以后，你会发现它并不神秘。
            """
        ),
        code(
            """
            from pathlib import Path

            SERVER_PATH = Path("/Users/siji/Desktop/AI/mcp/src/mcp_course/server.py")
            SERVER_PATH.exists()
            """
        ),
        code(
            """
            import asyncio
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client


            async def inspect_server():
                server_params = StdioServerParameters(
                    command="python",
                    args=[str(SERVER_PATH)],
                )

                async with stdio_client(server_params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        resources = await session.list_resources()
                        prompts = await session.list_prompts()
                        return tools, resources, prompts


            tools, resources, prompts = asyncio.run(inspect_server())
            len(tools.tools), len(resources.resources), len(prompts.prompts)
            """
        ),
        code(
            """
            [tool.name for tool in tools.tools]
            """
        ),
        code(
            """
            [resource.uri for resource in resources.resources]
            """
        ),
        code(
            """
            [prompt.name for prompt in prompts.prompts]
            """
        ),
        code(
            """
            async def call_one_tool():
                server_params = StdioServerParameters(
                    command="python",
                    args=[str(SERVER_PATH)],
                )

                async with stdio_client(server_params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        result = await session.call_tool(
                            "days_between",
                            {"start_date": "2026-04-20", "end_date": "2026-05-01"},
                        )
                        return result


            asyncio.run(call_one_tool())
            """
        ),
        md(
            """
            ## 这一步真正发生了什么

            你刚才虽然只写了几行代码，但背后已经完成了完整的一次协议流程：

            - client 启动 server 进程
            - 双方建立通信通道
            - client 发送初始化请求
            - client 请求列出能力
            - client 调用其中某个能力
            - server 返回结构化结果
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **先学 client，再学 server，会更容易理解 MCP 到底在解决什么问题。**
            2. **`list_tools()` / `list_resources()` / `list_prompts()` 本质上就是“能力发现”。**
            3. **当你能稳定完成 initialize -> list -> call，这条链路就已经通了。**
            """
        ),
    ],
)

write_notebook(
    "mcp_04_build_mcp_server.ipynb",
    [
        md(
            """
            # MCP 第 04 课：从零写一个真正可运行的 MCP Server

            前面三课是在建立心智模型，这一课开始动手。

            我们直接用官方 Python SDK 里的 `FastMCP` 来写一个 server。
            """
        ),
        md(
            """
            ## 1. 引入 SDK

            官方 Python SDK 提供了一个非常顺手的高层接口：`FastMCP`。

            它会帮你处理很多协议层细节，让你把注意力集中在“我到底想暴露什么能力”上。
            """
        ),
        code(
            """
            from mcp.server.fastmcp import FastMCP

            mcp = FastMCP("Demo Server", json_response=True)
            """
        ),
        md(
            """
            ## 2. 先加一个 tool

            这是最容易理解的一步。
            """
        ),
        code(
            """
            @mcp.tool()
            def add(a: int, b: int) -> int:
                \"\"\"Add two integers.\"\"\"
                return a + b
            """
        ),
        md(
            """
            ## 3. 再加一个 resource

            resource 的关键不是“像函数”，而是“像一个可读取入口”。
            """
        ),
        code(
            """
            @mcp.resource("course://outline")
            def get_course_outline() -> str:
                \"\"\"Read the course outline.\"\"\"
                return "1. Intro\\n2. Primitives\\n3. Client\\n4. Server"
            """
        ),
        md(
            """
            ## 4. 再加一个 prompt

            这能让你的 server 不只是暴露“数据”和“动作”，还暴露“交互模板”。
            """
        ),
        code(
            """
            @mcp.prompt()
            def explain_mcp(topic: str, audience: str = "beginner") -> str:
                \"\"\"Build a reusable teaching prompt.\"\"\"
                return f"Explain {topic} for a {audience} in clear Chinese."
            """
        ),
        md(
            """
            ## 5. 运行 server

            对于本地开发，我们直接用默认的 `stdio` transport 就够了。
            """
        ),
        code(
            """
            if __name__ == "__main__":
                mcp.run()
            """
        ),
        md(
            """
            ## 6. 看完整代码

            真正可运行的完整实现已经放在这里：

            `src/mcp_course/server.py`

            你可以直接打开它，也可以直接运行它。
            """
        ),
        code(
            """
            from pathlib import Path

            server_path = Path("/Users/siji/Desktop/AI/mcp/src/mcp_course/server.py")
            print(server_path)
            print(server_path.read_text()[:1200])
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **写 MCP server 的难点通常不在 SDK，而在能力建模。**
            2. **先做一个 `stdio` 版本是最稳妥的起点。**
            3. **一个好的教学 server 要故意同时覆盖 tool / resource / prompt 三种能力。**
            """
        ),
    ],
)

write_notebook(
    "mcp_05_llm_with_mcp.ipynb",
    [
        md(
            """
            # MCP 第 05 课：让本地 LLM 通过 MCP 使用工具

            到这里，MCP 的 server 和 client 我们都已经有了。

            最后一步就是回答一个非常实际的问题：

            > 怎么让本地部署的 LLM，真正通过 MCP 去使用工具？
            """
        ),
        md(
            """
            ## 这节课的策略

            一个常见做法是：

            1. 用 MCP client 连接 server，拿到工具描述
            2. 把这些工具描述转换成 OpenAI tool schema
            3. 发给本地 OpenAI 兼容模型
            4. 如果模型返回 tool call，就再通过 MCP client 真正执行
            5. 把结果送回模型，拿最终答案

            这本质上就是“LLM + MCP bridge”。
            """
        ),
        code(
            """
            import os
            from dotenv import load_dotenv

            load_dotenv("/Users/siji/Desktop/AI/mcp/.env")

            BASE_URL = os.getenv("OPENAI_BASE_URL", "http://10.0.0.63:1234/v1")
            API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
            MODEL = os.getenv("OPENAI_MODEL", "qwen/qwen3.6-35b-a3b")

            BASE_URL, MODEL
            """
        ),
        code(
            """
            from openai import OpenAI

            client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
            [m.id for m in client.models.list().data][:10]
            """
        ),
        md(
            """
            ## 把 MCP tools 转成 OpenAI tools

            如果一个本地模型支持 OpenAI 风格的 tool calling，这一步就能把 MCP server 暴露的能力“翻译”给它。
            """
        ),
        code(
            """
            import asyncio
            from pathlib import Path
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            SERVER_PATH = Path("/Users/siji/Desktop/AI/mcp/src/mcp_course/server.py")


            def to_openai_tools(mcp_tools):
                out = []
                for tool in mcp_tools:
                    out.append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description or "",
                                "parameters": tool.inputSchema,
                            },
                        }
                    )
                return out


            async def fetch_tools():
                params = StdioServerParameters(command="python", args=[str(SERVER_PATH)])
                async with stdio_client(params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        return tools.tools


            mcp_tools = asyncio.run(fetch_tools())
            openai_tools = to_openai_tools(mcp_tools)
            openai_tools[0]
            """
        ),
        md(
            """
            ## 看完整桥接实现

            配套文件已经放在：

            `src/mcp_course/llm_bridge.py`

            它做的事情就是：

            - 连上 MCP server
            - 取出 tools
            - 发给本地 LLM
            - 执行模型请求的 tool call
            - 再把结果发回模型
            """
        ),
        code(
            """
            from pathlib import Path

            bridge_path = Path("/Users/siji/Desktop/AI/mcp/src/mcp_course/llm_bridge.py")
            print(bridge_path)
            print(bridge_path.read_text()[:1800])
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **MCP 解决的是“能力标准化暴露”，LLM 解决的是“何时该用这些能力”。**
            2. **bridge 的本质是翻译层：MCP schema -> LLM 能理解的 tool schema。**
            3. **如果你的本地模型 tool calling 不稳定，也可以退回文本协议，但 MCP server 仍然有价值。**
            """
        ),
    ],
)
