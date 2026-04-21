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


            tools, resources, prompts = await inspect_server()
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


            await call_one_tool()
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


            mcp_tools = await fetch_tools()
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

write_notebook(
    "mcp_06_function_calling_deep_dive.ipynb",
    [
        md(
            """
            # MCP 第 06 课：Function Calling 深入，模型到底在“调用”什么

            到这里你已经知道 MCP 和 tool use 的基本关系了。

            这一课我们聚焦一个更细的点：

            > 当我们说模型在“function calling”时，真正发生的到底是什么？

            最重要的答案是：

            **模型并没有直接执行函数，它只是生成了一个结构化的“调用意图”。**
            """
        ),
        md(
            """
            ## 1. Function Calling 的三层

            你可以把它拆成三层：

            - 模型层：根据上下文判断要不要调用工具
            - 协议层：把调用意图输出成结构化数据
            - 执行层：你的程序真正执行函数、命令或 API

            很多初学者把这三层混在一起，所以会误以为“模型自己能执行工具”。
            """
        ),
        md(
            """
            ## 2. 一个最小 schema

            绝大多数 function calling 都离不开这几部分：

            - `name`
            - `description`
            - `parameters` / JSON Schema

            schema 的任务不是“给人看”，而是**约束模型输出的参数形状**。
            """
        ),
        code(
            """
            weather_tool = {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather for a city.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"},
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["city"],
                    },
                },
            }

            weather_tool
            """
        ),
        md(
            """
            ## 3. `tool_choice` 的含义

            这是非常关键但经常被忽略的控制项。

            常见模式：

            - `auto`：模型自己决定要不要调工具
            - `required`：必须至少调一个工具
            - 指定某个工具：强制调用某个具体函数

            它本质上是在控制“模型的决策自由度”。
            """
        ),
        code(
            """
            examples = {
                "auto": "让模型自己判断是否需要工具",
                "required": "要求模型必须走工具链路",
                "specific_tool": "例如强制使用 get_weather",
            }

            examples
            """
        ),
        md(
            """
            ## 4. 为什么参数约束很重要

            真实工程里，参数 schema 至少解决四件事：

            - 减少参数名漂移
            - 限制枚举值
            - 明确必填字段
            - 为执行层做前置验证

            schema 写得越松，执行层越痛苦。
            """
        ),
        code(
            """
            strict_tool = {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "mode": {"type": "string", "enum": ["read", "write"]},
                },
                "required": ["path", "mode"],
                "additionalProperties": False,
            }

            strict_tool
            """
        ),
        md(
            """
            ## 5. 并行 tool calls 和串行 tool calls

            有些任务天然适合并行：

            - 同时查多个城市天气
            - 同时读多个文档片段

            有些任务必须串行：

            - 先搜索文件，再决定改哪个文件
            - 先跑测试，再根据失败结果修代码

            **是否并行，取决于数据依赖，而不是取决于你有没有多个工具。**
            """
        ),
        md(
            """
            ## 6. 失败、重试与幂等性

            真正难的地方不在“第一次调用成功”，而在失败之后怎么办。

            你至少要问：

            - 这个工具能安全重试吗？
            - 它有副作用吗？
            - 失败时要把什么信息回给模型？

            读型工具通常更容易重试，写型工具要更谨慎。
            """
        ),
        md(
            """
            ## 7. 和 MCP 的关系

            Function calling 更像“模型怎么表达想调用工具”。

            MCP 更像“应用和外部能力之间怎么标准化通信”。

            两者不是替代关系，常常是上下两层：

            - 上层 LLM 用 function calling 做决策
            - 下层执行用 MCP 去发现和调用实际能力
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **Function calling 的本质是“结构化意图输出”，不是模型直接执行。**
            2. **schema 既是提示词的一部分，也是执行层的防线。**
            3. **复杂工具链路真正的难点在重试、回填、幂等和权限。**
            """
        ),
    ],
)

write_notebook(
    "mcp_07_shell_and_cli_tools.ipynb",
    [
        md(
            """
            # MCP 第 07 课：Shell / CLI 工具，为什么它既强大又危险

            如果说 API 工具是专用工具，那么 shell/CLI 几乎就是“通用超工具”。

            它强的地方在于：

            - 能读文件
            - 能搜代码
            - 能跑测试
            - 能调用现成命令行程序

            但它危险也正危险在这里。
            """
        ),
        md(
            """
            ## 1. Shell 工具的基本模式

            在 agent 系统里，shell 工具通常不是“模型自己执行命令”，而是：

            1. 模型提出命令
            2. 宿主程序决定是否执行
            3. 把输出再返回给模型

            OpenAI 官方也把 `shell` 设计成这种模式，而不是让模型直接接管机器。
            """
        ),
        code(
            """
            allowed_examples = [
                "pwd",
                "rg --files src",
                "pytest tests/test_api.py",
                "git status --short",
            ]

            allowed_examples
            """
        ),
        md(
            """
            ## 2. 为什么 CLI 对 coding agent 特别重要

            因为代码工作天然依赖大量命令行能力：

            - 搜索：`rg`
            - 构建：`npm build` / `cargo build`
            - 测试：`pytest` / `npm test`
            - 版本控制：`git status` / `git diff`
            - 格式化：`ruff format` / `prettier`

            没有 CLI，coding agent 的“手脚”会少很多。
            """
        ),
        md(
            """
            ## 3. 一个最小命令白名单心智模型

            你可以把 shell tool 想成三层防线：

            - 允许哪些命令
            - 允许在哪些目录执行
            - 是否需要人类审批

            这三层缺任何一层，风险都会急剧上升。
            """
        ),
        code(
            """
            policy = {
                "allow": ["pwd", "ls", "rg", "pytest", "git status", "git diff"],
                "deny": ["rm -rf /", "curl | sh", "git push --force"],
                "require_confirmation": ["git commit", "git push", "pip install"],
            }

            policy
            """
        ),
        md(
            """
            ## 4. 读型 CLI 和写型 CLI

            这是一个特别实用的分类：

            - 读型：`ls`、`rg`、`cat`、`git status`
            - 写型：`mv`、`git commit`、`sed -i`
            - 高危型：`rm`、`sudo`、联网下载执行

            实际系统里，这三类通常要配不同权限。
            """
        ),
        md(
            """
            ## 5. Codex / Claude Code 为什么都很重视 CLI

            因为它们不是“回答编程问题”，而是“在真实开发环境里完成工作”。

            一旦目标是完成真实工作，就离不开：

            - 文件系统
            - 终端
            - 测试工具
            - 包管理器
            - git
            """
        ),
        md(
            """
            ## 6. CLI 不是万能的

            shell 很强，但不代表所有能力都该塞给 shell。

            当某个能力有明确结构时，单独做成专用工具往往更好：

            - 参数更清晰
            - 更容易校验
            - 更容易审计
            - 更容易做权限控制
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **CLI 是 coding agent 的核心执行界面之一。**
            2. **shell 工具最需要白名单、目录限制和审批流。**
            3. **能专门化的能力，尽量别全部退化成“跑一条命令”。**
            """
        ),
    ],
)

write_notebook(
    "mcp_08_tool_use_patterns.ipynb",
    [
        md(
            """
            # MCP 第 08 课：Tool Use 设计模式，工具不是越多越好

            这一课讨论的是“工具架构”，不是某个具体 SDK。

            当你开始做真实 agent 系统时，很快会遇到这些问题：

            - 工具应该切多细？
            - 什么该做成 tool，什么该做成 resource？
            - 模型失败时怎么回填信息？
            """
        ),
        md(
            """
            ## 1. 粒度设计

            工具过粗：

            - 模型不容易学会稳定使用
            - 参数很复杂
            - 错误难定位

            工具过细：

            - 工具数量爆炸
            - 路由成本变高
            - 多步编排更脆弱

            好的粒度通常对应“一个稳定可解释的动作”。
            """
        ),
        md(
            """
            ## 2. Read / Write / Act

            一个很实用的分类法是：

            - Read：读取信息
            - Write：修改状态
            - Act：触发动作或流程

            这三类不只是语义不同，风险级别也不同。
            """
        ),
        code(
            """
            tool_classes = {
                "read": ["search_docs", "read_file", "query_db"],
                "write": ["update_ticket", "edit_file", "write_db"],
                "act": ["deploy_service", "send_email", "restart_worker"],
            }

            tool_classes
            """
        ),
        md(
            """
            ## 3. 先 resource，后 tool

            很多知识型场景里，先让模型读资源，再决定要不要调用动作工具，会更稳。

            例如：

            - 先读运行手册，再决定是否重启服务
            - 先读代码，再决定是否修改文件
            - 先读 FAQ，再决定是否发起工单
            """
        ),
        md(
            """
            ## 4. 错误回填的质量，决定 agent 上限

            一个差的错误回填：

            - “tool failed”

            一个好的错误回填：

            - 哪个参数错了
            - 错在什么格式
            - 当前可选值是什么
            - 建议下一步怎么修正

            模型是否能自我修复，很大程度取决于你怎么回填错误。
            """
        ),
        md(
            """
            ## 5. 工具选择不是纯技术问题

            很多时候真正要权衡的是：

            - 成本
            - 延迟
            - 失败率
            - 审计需求
            - 权限风险

            所以工具架构本质上也是产品设计。
            """
        ),
        md(
            """
            ## 6. MCP 在这里的价值

            当工具越来越多时，MCP 的价值开始变明显：

            - 标准化能力发现
            - 标准化参数与返回
            - 标准化资源和 prompt 暴露
            - 降低多系统集成成本
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **工具设计的核心是粒度、权限和错误回填。**
            2. **知识型任务先读 resource，动作型任务再调 tool，通常更稳。**
            3. **工具架构做得好，模型能力才容易被放大。**
            """
        ),
    ],
)

write_notebook(
    "mcp_09_memory_skills_sop.ipynb",
    [
        md(
            """
            # MCP 第 09 课：Memory、Skill、SOP，Agent 产品层真正拉开差距的地方

            到这一步，我们开始离开“协议”和“工具函数”，进入 agent 产品设计层。

            很多强大的 coding agent，差距并不只在模型，而在这些层：

            - 它记住了什么
            - 它复用了什么套路
            - 它按什么流程做事
            """
        ),
        md(
            """
            ## 1. Memory 是什么

            `memory` 更接近“持续存在的上下文约定”。

            例如：

            - 这个仓库用什么测试命令
            - 团队偏好的代码风格
            - 哪些目录不能动
            - 用户的长期偏好

            它回答的是：**以后遇到类似情况，agent 应该默认记住什么。**
            """
        ),
        md(
            """
            ## 2. Skill 是什么

            `skill` 更接近“可复用能力包”。

            它通常包含：

            - 一段专门化指令
            - 某类任务的工作流
            - 推荐工具使用方式
            - 可能还带模板或脚本

            它回答的是：**做这类事时，agent 应该套用哪种专业套路。**
            """
        ),
        md(
            """
            ## 3. SOP 是什么

            `SOP` 是标准操作流程。

            它更强调顺序和检查点，例如：

            1. 先读需求
            2. 再读相关代码
            3. 再制定改动计划
            4. 修改后跑测试
            5. 最后汇报风险

            它回答的是：**这类任务应该按什么节奏完成。**
            """
        ),
        code(
            """
            concepts = {
                "memory": "长期约定",
                "skill": "可复用能力包",
                "sop": "标准执行流程",
            }

            concepts
            """
        ),
        md(
            """
            ## 4. 三者的关系

            一个很实用的理解方式：

            - Memory：保存默认背景
            - Skill：提供专业能力
            - SOP：约束执行步骤

            它们常常一起工作，而不是互斥。
            """
        ),
        md(
            """
            ## 5. 为什么 coding agent 特别依赖这三层

            因为 coding 任务不是一次性问答，而是持续协作：

            - 项目约定会反复出现
            - 常见任务模式会反复出现
            - 验证流程必须重复执行

            没有 memory / skill / SOP，agent 很难长期稳定。
            """
        ),
        md(
            """
            ## 6. 它们通常不是 MCP 标准字段

            这是个容易混淆的点。

            MCP 主要定义的是能力暴露与通信协议。

            memory / skill / SOP 更多是**agent 产品层、运行时层、团队协作层**的概念。
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **Memory 解决“一直记住什么”，Skill 解决“怎么专业地做”，SOP 解决“按什么步骤做”。**
            2. **很多 agent 产品差距，实际上来自这三层设计，而不只是模型本身。**
            3. **协议层让能力可接，产品层才让能力可持续复用。**
            """
        ),
    ],
)

write_notebook(
    "mcp_10_coding_agents_codex_claude_code.ipynb",
    [
        md(
            """
            # MCP 第 10 课：Codex、Claude Code 这类 Coding Agent，到底在系统层做了什么

            很多人第一次看到 Codex 或 Claude Code，会以为它们只是“会写代码的聊天机器人”。

            其实更准确的说法是：

            **它们是“模型 + 工具运行时 + 权限系统 + 记忆机制 + 工作流”的组合产品。**
            """
        ),
        md(
            """
            ## 1. 先看一张抽象结构图

            ```text
            User
              ->
            Agent Runtime
              ->
            Model decision + tools + memory + permissions
              ->
            Files / CLI / MCP / APIs / Git / Tests
            ```

            真正完成工作的，不只是模型，还包括外围运行时。
            """
        ),
        md(
            """
            ## 2. Codex 这类系统强调什么

            从官方资料看，Codex 强调这些点：

            - 读、改、执行代码
            - 在本地或云端环境里工作
            - 能连接 MCP server
            - 能处理并行任务与背景任务

            所以它不是单纯“生成代码”，而是“在工程环境中完成任务”。
            """
        ),
        md(
            """
            ## 3. Claude Code 这类系统强调什么

            Claude Code 很突出的一点是把很多产品层概念显式化了：

            - `/mcp`
            - `/memory`
            - `/agents`
            - `/permissions`
            - slash commands

            这让用户能更直接看到“agent runtime”到底有哪些部件。
            """
        ),
        md(
            """
            ## 4. 它们和普通 chat app 的区别

            普通 chat app 的主要职责是“回答”。

            coding agent 的主要职责是“完成任务”。

            一旦目标从回答变成完成任务，系统就必须补齐：

            - 工具
            - 状态
            - 权限
            - 验证
            - 工作日志
            """
        ),
        md(
            """
            ## 5. MCP 在这些产品里扮演什么角色

            MCP 的价值是把“外部能力接入”标准化。

            所以对于 Codex、Claude Code 这类系统，MCP 像一个标准接口层：

            - 工具怎么发现
            - 资源怎么读取
            - prompts 怎么暴露
            - 不同系统怎么复用同一套能力
            """
        ),
        md(
            """
            ## 6. 你以后看这类产品时，优先看什么

            与其先问“它用的是什么模型”，不如先问：

            - 它有哪些工具？
            - 权限怎么控？
            - 有长期记忆吗？
            - 能否接 MCP？
            - 是否有验证和回顾流程？

            这几个问题往往更决定真实使用体验。
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **Coding agent 是系统产品，不只是模型产品。**
            2. **工具、权限、记忆、验证这几层，决定了它能不能完成真实工作。**
            3. **MCP 的意义在于把外部能力接入从“手搓集成”变成“标准接口”。**
            """
        ),
    ],
)

write_notebook(
    "mcp_11_planning_verification_and_reflection.ipynb",
    [
        md(
            """
            # MCP 第 11 课：Planning、Verification、Reflection，Agent 为什么能做复杂工作

            真正的复杂任务，几乎从来不是“一次提示词 + 一次工具调用”就结束。

            它更像一个循环：

            `Plan -> Act -> Observe -> Verify -> Reflect -> Continue or Stop`
            """
        ),
        md(
            """
            ## 1. Planning：先拆任务

            复杂任务最怕的一件事，是还没搞清楚结构就开始乱做。

            planning 的价值在于：

            - 拆分子问题
            - 识别依赖关系
            - 识别风险和未知项
            - 决定哪些步骤该先做
            """
        ),
        code(
            """
            plan = [
                "读 README 和相关代码",
                "定位 bug 或需求边界",
                "决定修改方案",
                "实现改动",
                "跑测试和静态检查",
                "总结风险与结果",
            ]

            plan
            """
        ),
        md(
            """
            ## 2. Verification：不要只相信模型自己的判断

            agent 想真正可靠，必须引入外部验证。

            常见验证手段：

            - 跑测试
            - 编译
            - schema 校验
            - 对比前后输出
            - 人工 review

            **没有 verification，复杂工作基本不可托付。**
            """
        ),
        md(
            """
            ## 3. Reflection：失败之后怎么变聪明

            reflection 不是让模型“多想一会儿”这么简单。

            它更像：

            - 回顾刚才哪一步错了
            - 为什么错
            - 之后要调整什么策略

            这会显著提升多步任务的稳定性。
            """
        ),
        md(
            """
            ## 4. 一个很实用的循环

            对 coding / ops / research 类 agent，很常见的循环是：

            1. 先搜集上下文
            2. 再形成局部计划
            3. 执行一步
            4. 验证结果
            5. 根据验证结果修正下一步

            这比“先写一个超完整计划再一次性执行”通常更稳。
            """
        ),
        md(
            """
            ## 5. 为什么这和 MCP 有关

            因为 planning / verification / reflection 都离不开外部能力。

            例如：

            - planning 需要读资源
            - verification 需要调测试工具
            - reflection 需要结合执行结果重新决策

            MCP 让这些外部能力更容易标准化接入。
            """
        ),
        md(
            """
            ## 6. 复杂工作不是“更强的单次回答”

            这是最重要的一点。

            复杂工作能力更多来自：

            - 循环
            - 工具
            - 验证
            - 记忆
            - 流程控制

            而不只是更长、更强的单次生成。
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **复杂任务的关键不是一次答对，而是能在循环中不断纠正。**
            2. **verification 是把 agent 从“看起来聪明”变成“更可信”的核心步骤。**
            3. **planning、tools、verification、reflection 共同构成 agent 的工作闭环。**
            """
        ),
    ],
)

write_notebook(
    "mcp_12_safe_file_agent.ipynb",
    [
        md(
            """
            # MCP 第 12 课：Safe File Agent，为什么 read-only agent 是最好的起点

            如果你准备自己做 agent，最推荐的第一个真实系统，往往不是“自动改代码”，而是：

            **只读文件助手。**

            它的价值非常大，因为它能帮你练到这些核心能力：

            - 工具选择
            - 上下文收集
            - 路由与总结
            - 权限边界
            """
        ),
        md(
            """
            ## 1. 为什么先做 read-only

            因为 read-only agent 有几个天然优点：

            - 风险低
            - 调试简单
            - 出错代价小
            - 仍然足够真实

            你可以让它：

            - 列目录
            - 搜文件
            - 读文件
            - 总结结构
            - 回答“某段逻辑在哪里”
            """
        ),
        md(
            """
            ## 2. 最小工具集

            一个安全文件助手，最小工具集通常就够了：

            - `list_dir(path)`
            - `search_files(query)`
            - `read_file(path)`
            - `read_file_chunk(path, start, end)`

            注意这里没有任何写操作。
            """
        ),
        code(
            """
            read_only_tools = [
                "list_dir(path)",
                "search_files(query)",
                "read_file(path)",
                "read_file_chunk(path, start, end)",
            ]

            read_only_tools
            """
        ),
        md(
            """
            ## 3. 一个好的 read-only agent 会怎么工作

            面对“帮我找到登录逻辑在哪”这类问题，它通常应该：

            1. 先搜文件或关键词
            2. 再读候选文件
            3. 再缩小范围
            4. 最后给出结论和证据

            也就是说，它不是一上来就“猜”，而是先搜集证据。
            """
        ),
        md(
            """
            ## 4. 为什么这类系统很适合创新

            因为你可以在很多地方做产品创新：

            - 搜索排序
            - 自动摘要方式
            - 引用证据格式
            - 多文件聚合阅读
            - 用户追问链路

            这类创新不一定靠更强模型，也可以靠更好的工作流设计。
            """
        ),
        md(
            """
            ## 5. 最常见的失败点

            read-only agent 虽然安全，但并不代表它天然可靠。

            常见失败点：

            - 搜索召回不足
            - 读了错文件
            - 读的上下文太短
            - 过早下结论
            - 引用证据不清楚
            """
        ),
        md(
            """
            ## 6. 为什么它是复杂项目的地基

            任何写型 agent、coding agent、ops agent，在动手之前几乎都先要做 read-only 调研。

            所以你把这个阶段打稳，后面升级成可写 agent 会容易很多。
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **read-only agent 是最适合打基础的真实 agent 形态。**
            2. **复杂系统的第一步通常不是修改，而是可靠地搜集上下文。**
            3. **很多创新点来自检索、摘要、引用和交互设计，而不只是模型本身。**
            """
        ),
    ],
)

write_notebook(
    "mcp_13_shell_coding_agent.ipynb",
    [
        md(
            """
            # MCP 第 13 课：Shell Coding Agent，代码代理的最小闭环是什么

            当你从 read-only 往前走一步，很自然就会来到 coding agent。

            一个最小可用的 coding agent 闭环通常是：

            `搜代码 -> 读代码 -> 改代码 -> 跑测试 -> 总结结果`
            """
        ),
        md(
            """
            ## 1. 为什么 coding agent 离不开 shell

            因为真正的软件工程上下文，大量存在于命令行里：

            - 代码搜索
            - 测试执行
            - 构建
            - lint
            - git diff

            所以 coding agent 的“执行骨架”通常就是 shell。
            """
        ),
        code(
            """
            coding_loop = [
                "rg / read relevant files",
                "edit target files",
                "run tests",
                "inspect failures",
                "iterate or stop",
            ]

            coding_loop
            """
        ),
        md(
            """
            ## 2. 最小工具集

            从工程角度看，一个朴素但够用的 coding agent 只需要这些能力：

            - 搜索文件
            - 读取文件
            - 编辑文件
            - 执行测试或命令
            - 查看 diff

            这其实就是很多 coding agent 产品的最小核心。
            """
        ),
        md(
            """
            ## 3. 为什么“验证”在 coding agent 里更重要

            因为 coding 任务很容易出现“看起来合理，但实际跑不通”的情况。

            所以 coding agent 最重要的外部真相来源通常是：

            - 单元测试
            - 构建结果
            - 类型检查
            - linter
            - 运行日志
            """
        ),
        md(
            """
            ## 4. 一个成熟 coding agent 的关键差异点

            真正拉开差距的往往不是会不会改文件，而是：

            - 上下文收集是否高效
            - 改动范围是否克制
            - 会不会主动验证
            - 失败后会不会调整策略
            - 汇报是否清楚
            """
        ),
        md(
            """
            ## 5. 最值得创新的地方

            你以后做复杂项目时，很适合创新这些位置：

            - 自动定位相关代码的策略
            - 局部 patch 的生成方式
            - 测试选择策略
            - 失败后的自修复循环
            - 改动解释和风险提示
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **coding agent 的最小闭环是“读、改、测、复盘”。**
            2. **shell 之所以重要，是因为工程事实大量暴露在 CLI 里。**
            3. **好的 coding agent，重点不在多改，而在少错、可验证、可解释。**
            """
        ),
    ],
)

write_notebook(
    "mcp_14_agent_evaluation.ipynb",
    [
        md(
            """
            # MCP 第 14 课：Agent Evaluation，没有评估就没有工程

            这一课非常关键。

            如果说前面是在学“怎么做 agent”，那这一课是在学：

            > 怎么知道它到底做得好不好。
            """
        ),
        md(
            """
            ## 1. 为什么 agent 评估比普通问答更难

            因为 agent 不是只有一个最终答案。

            它中间还包含：

            - 工具选择
            - 参数填写
            - 多步决策
            - 错误恢复
            - 最终验证

            所以你不能只看最后一句话像不像对。
            """
        ),
        md(
            """
            ## 2. 评估要拆层

            一个实用的拆法是：

            - Step-level：每一步动作对不对
            - Tool-level：工具选得对不对、参数对不对
            - Outcome-level：最后结果对不对
            - Cost-level：花了多少时间、多少 token、多少命令
            """
        ),
        code(
            """
            eval_axes = [
                "tool selection",
                "argument correctness",
                "verification success",
                "final correctness",
                "cost and latency",
            ]

            eval_axes
            """
        ),
        md(
            """
            ## 3. 一个常见误区

            很多人只做 demo 验证：

            - 挑几个容易例子
            - 跑通一次
            - 感觉不错

            这不叫评估，这叫演示。

            真正的评估需要样本集、标准、记录和复盘。
            """
        ),
        md(
            """
            ## 4. Agent 最值得测的指标

            对工具型 agent，最值得优先测的是：

            - 是否调用了正确工具
            - 参数是否正确
            - 是否少走弯路
            - 是否进行了必要验证
            - 是否在失败后恢复
            """
        ),
        md(
            """
            ## 5. 离线评估和在线评估

            两者都重要：

            - 离线评估：固定样本集，便于比较版本
            - 在线评估：真实用户场景，更能暴露边角问题

            工程里通常是离线做回归，在线看真实表现。
            """
        ),
        md(
            """
            ## 6. 为什么评估也是创新空间

            很多团队只卷模型，但真正难的是：

            - 数据集怎么建
            - 失败类型怎么分
            - 如何定位瓶颈
            - 如何把失败反馈到产品设计

            评估体系本身，就是 agent 产品竞争力的一部分。
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **没有评估的 agent，很难从 demo 变成系统。**
            2. **工具型 agent 的评估必须拆到 tool、step 和 outcome 多层。**
            3. **好的评估不仅是打分，更是发现瓶颈和指导迭代。**
            """
        ),
    ],
)

write_notebook(
    "mcp_15_agent_safety_and_permissions.ipynb",
    [
        md(
            """
            # MCP 第 15 课：Safety 与 Permissions，Agent 不是越能干越好

            做 agent 时，一个特别危险的误区是：

            > “给它更多权限，它就更强。”

            实际上更准确的说法是：

            **权限越大，收益和风险都会一起上升。**
            """
        ),
        md(
            """
            ## 1. 权限设计的核心问题

            你真正要回答的是：

            - 它能读什么
            - 它能改什么
            - 它能联网到哪里
            - 它能执行哪些命令
            - 哪些动作必须人工确认
            """
        ),
        md(
            """
            ## 2. 一个很实用的权限分层

            你可以把 agent 权限粗分成：

            - Read-only
            - Write-limited
            - High-risk actions with approval

            这比简单的“能不能用工具”更接近真实系统。
            """
        ),
        code(
            """
            permission_levels = {
                "read_only": ["read files", "search", "list resources"],
                "write_limited": ["edit whitelisted files", "create patch"],
                "approval_required": ["deploy", "git push", "delete data"],
            }

            permission_levels
            """
        ),
        md(
            """
            ## 3. Prompt Injection 为什么危险

            一旦 agent 会读外部内容、再调用工具，就会遇到这个风险：

            - 外部内容里藏了恶意指令
            - 模型把这些指令当真
            - 最后触发越权动作

            所以“读到的内容”不能天然被视为可信。
            """
        ),
        md(
            """
            ## 4. 安全不只是拦命令

            真正的 agent 安全通常包含：

            - 沙箱
            - 最小权限
            - 明确审批点
            - 输出审计
            - 网络限制
            - secret 隔离
            """
        ),
        md(
            """
            ## 5. 为什么权限架构本身就是产品设计

            用户体验和安全并不是完全对立的。

            一个好的系统会让用户清楚知道：

            - 当前 agent 能做什么
            - 不能做什么
            - 哪一步需要确认
            - 为什么需要确认
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **agent 能力设计，本质上也是权限设计。**
            2. **真正危险的系统不是工具多，而是边界不清。**
            3. **安全最好从第一天就内建，而不是最后再补。**
            """
        ),
    ],
)

write_notebook(
    "mcp_16_memory_lifecycle.ipynb",
    [
        md(
            """
            # MCP 第 16 课：Memory Lifecycle，记忆不是越多越好

            前面我们讲过 memory 的概念，这一课继续往下走：

            > 记忆应该怎么产生、更新、冲突、淘汰？

            这就是 memory lifecycle。
            """
        ),
        md(
            """
            ## 1. 不是所有信息都值得记住

            一个成熟的 memory 系统，首先要能区分：

            - 临时任务上下文
            - 项目级长期约定
            - 用户级偏好
            - 可能过期的事实

            如果全都混在一起，记忆会快速污染。
            """
        ),
        md(
            """
            ## 2. 记忆的常见生命周期

            一个典型流程是：

            1. 候选信息出现
            2. 判断是否值得记忆
            3. 写入某个记忆层
            4. 后续任务中检索
            5. 发现冲突时更新或淘汰
            """
        ),
        code(
            """
            memory_lifecycle = [
                "capture",
                "filter",
                "store",
                "retrieve",
                "update or evict",
            ]

            memory_lifecycle
            """
        ),
        md(
            """
            ## 3. 最容易出问题的地方

            memory 系统常见问题包括：

            - 记了太多琐碎信息
            - 旧信息没有过期
            - 用户偏好和项目约定混淆
            - 错误记忆被长期保留
            """
        ),
        md(
            """
            ## 4. 一个很实用的划分法

            可以把记忆粗分成三层：

            - Session memory：当前会话临时上下文
            - Project memory：项目长期约定
            - User memory：用户长期偏好

            三层不要混着存。
            """
        ),
        md(
            """
            ## 5. 记忆也要可审计

            很多系统只考虑“怎么记”，没考虑“怎么查”。

            但真实产品里你最好能回答：

            - 这条记忆从哪来的
            - 什么时候写入的
            - 为什么被采用
            - 如何修改或删除
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **memory 的关键不是存，而是筛选、分层和更新。**
            2. **错误的长期记忆，会持续拉低 agent 质量。**
            3. **memory lifecycle 设计得好，agent 才能真正长期协作。**
            """
        ),
    ],
)

write_notebook(
    "mcp_17_multi_agent_workflows.ipynb",
    [
        md(
            """
            # MCP 第 17 课：Multi-Agent Workflows，什么时候多代理真的有价值

            学到这里，很多人会自然开始想：

            > 要不要把一个 agent 拆成多个？

            正确答案通常不是“越多越好”，而是：

            **只有当分工能明显降低复杂度时，多代理才有价值。**
            """
        ),
        md(
            """
            ## 1. 单代理什么时候够用

            如果任务满足这些条件，单代理通常就够了：

            - 上下文不大
            - 工具不多
            - 步骤依赖简单
            - 不需要明显分工
            """
        ),
        md(
            """
            ## 2. 多代理什么时候更合适

            常见场景：

            - 研究和实现可以并行
            - 规划和执行适合分开
            - 审查和生成适合分开
            - 不同子任务需要不同专长
            """
        ),
        code(
            """
            roles = ["planner", "researcher", "executor", "reviewer"]
            roles
            """
        ),
        md(
            """
            ## 3. 多代理不是“多开几个模型”这么简单

            真正难的是：

            - 谁负责什么
            - 怎么交接信息
            - 怎么避免重复工作
            - 怎么汇总结论
            - 谁来做最后验证
            """
        ),
        md(
            """
            ## 4. 最常见的失败模式

            多代理系统很容易出现：

            - 角色边界不清
            - 上下文传递过多或过少
            - 多个 agent 重复探索
            - 没有统一的最终裁决
            """
        ),
        md(
            """
            ## 5. 为什么 workflow 往往比 agent 数量更重要

            很多系统看起来是“多代理很强”，实际上真正起作用的是：

            - 清晰的步骤编排
            - 合理的中间产物
            - 明确的检查点
            - 稳定的信息传递格式

            也就是说，强的是 workflow，不一定是 agent 数量。
            """
        ),
        md(
            """
            ## 6. 创新空间在哪里

            你以后做复杂项目时，很适合创新这些点：

            - 角色拆分方式
            - 子任务路由方式
            - 中间产物结构
            - 审查与验证机制
            - 并行和串行的调度策略
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **多代理的价值来自分工和 workflow，不来自“更多模型实例”。**
            2. **单代理先做稳，再考虑多代理，通常更合理。**
            3. **多代理系统的关键不是启动更多 agent，而是让它们协作得更清楚。**
            """
        ),
    ],
)

write_notebook(
    "mcp_18_observability_and_tracing.ipynb",
    [
        md(
            """
            # MCP 第 18 课：Observability 与 Tracing，看不见就很难优化

            当 agent 开始变复杂以后，一个问题会迅速出现：

            > 它到底刚才做了什么？

            如果看不见过程，你就很难回答：

            - 为什么它失败了
            - 为什么它慢
            - 为什么它成本高
            - 为什么它选错了工具
            """
        ),
        md(
            """
            ## 1. 什么叫 observability

            在 agent 系统里，observability 可以简单理解成：

            **你能不能清楚地看到 agent 的决策和执行轨迹。**

            这通常包括：

            - 读了哪些上下文
            - 调了哪些工具
            - 参数是什么
            - 返回了什么
            - 哪一步失败了
            """
        ),
        md(
            """
            ## 2. 为什么 tracing 特别重要

            `trace` 不是普通日志，它更像一条完整任务链。

            对一条复杂任务，你通常想看到：

            - 请求开始
            - 中间步骤
            - 每个工具调用
            - 验证结果
            - 最终输出

            没有 trace，你只会得到一堆分散日志。
            """
        ),
        code(
            """
            trace_example = [
                "user request received",
                "searched project files",
                "read 3 candidate files",
                "called test runner",
                "returned final answer",
            ]

            trace_example
            """
        ),
        md(
            """
            ## 3. 最值得记录的字段

            一个实用 trace 至少应该能回答：

            - 任务 id 是什么
            - 当前步骤是什么
            - 使用了哪个工具
            - 参数是什么
            - 成功还是失败
            - 耗时多少
            - 结果摘要是什么
            """
        ),
        md(
            """
            ## 4. 可观测性也是创新空间

            很多 agent 产品失败，不是因为模型不够强，而是因为团队根本看不清问题出在哪。

            如果你未来做项目，这些地方都值得创新：

            - 更易读的 trace 展示
            - 工具调用的可视化
            - 错误聚类
            - 回放与复盘
            - 用户可解释日志
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **看不见 agent 的执行过程，就很难真正优化它。**
            2. **trace 是复杂 agent 的基础设施，不是可有可无的附属品。**
            3. **可观测性越好，评估、调试、安全和产品体验都会一起变好。**
            """
        ),
    ],
)

write_notebook(
    "mcp_19_cost_latency_and_routing.ipynb",
    [
        md(
            """
            # MCP 第 19 课：Cost、Latency 与 Routing，Agent 不只是“能做”，还要“值得做”

            一旦 agent 开始真正工作，工程问题就会跳出来：

            - 太慢
            - 太贵
            - 调了太多没必要的工具
            - 每一步都用了过强模型

            所以这节课讨论的是“资源调度感”。
            """
        ),
        md(
            """
            ## 1. 三个永远在拉扯的目标

            几乎所有 agent 系统都在平衡这三件事：

            - 质量
            - 延迟
            - 成本

            很少有系统能在三者上同时最优。
            """
        ),
        md(
            """
            ## 2. Routing 是什么

            routing 可以理解成：

            **把不同任务、不同步骤路由到不同模型、工具或流程。**

            例如：

            - 简单问题走轻量模型
            - 复杂推理走强模型
            - 查文档走 resource
            - 精确计算走工具
            """
        ),
        code(
            """
            routing_examples = {
                "simple_lookup": "small model + search",
                "complex_bugfix": "strong model + shell + tests",
                "policy_question": "resource first, then answer",
            }

            routing_examples
            """
        ),
        md(
            """
            ## 3. 为什么 latency 会被低估

            很多系统单步看起来不慢，但一旦进入多轮 agent 循环：

            - 多次模型调用
            - 多次工具调用
            - 多次验证

            延迟会快速叠加。
            """
        ),
        md(
            """
            ## 4. 成本不只来自模型

            成本通常来自几类：

            - 模型 token
            - 工具调用
            - 外部 API
            - 容器 / 运行环境
            - 人工审核成本

            所以成本优化不能只盯着 prompt 长度。
            """
        ),
        md(
            """
            ## 5. 最值得优化的地方

            很多系统的高价值优化点在这里：

            - 提前终止无效循环
            - 减少重复上下文读取
            - 用更小模型做前置筛选
            - 把 read 和 write 流程分层
            - 把昂贵工具留给必要时再用
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **agent 设计不仅是能力设计，也是资源调度设计。**
            2. **routing 做得好，系统通常会同时更便宜、更快、更稳。**
            3. **真正贵的地方常常不是单步，而是多轮循环里的累计开销。**
            """
        ),
    ],
)

write_notebook(
    "mcp_20_human_in_the_loop.ipynb",
    [
        md(
            """
            # MCP 第 20 课：Human-in-the-Loop，人类不是 agent 的补丁，而是系统的一部分

            很多初学者会把人工介入理解成：

            “模型不够强，所以人来兜底。”

            但更成熟的理解是：

            **人类本来就是 agent 系统里的一个关键节点。**
            """
        ),
        md(
            """
            ## 1. 人为什么要在 loop 里

            因为有些判断天然更适合人：

            - 风险判断
            - 业务优先级
            - 最终发布
            - 替代方案取舍
            - 是否接受某个副作用
            """
        ),
        md(
            """
            ## 2. 常见的人机协作点

            一个成熟系统常见的人类介入点有：

            - 执行前确认
            - 方案二选一
            - 高风险动作审批
            - 失败后改方向
            - 最终结果 review
            """
        ),
        code(
            """
            hitl_points = [
                "approve write action",
                "choose between plans",
                "review final patch",
                "decide deployment timing",
            ]

            hitl_points
            """
        ),
        md(
            """
            ## 3. 好的人机协作，不是频繁打断

            如果 agent 每一步都来问你，那并不叫协作，而是叫低效。

            好的设计通常是：

            - 低风险动作自动做
            - 高风险动作集中确认
            - 给人看的是压缩后的关键信息
            """
        ),
        md(
            """
            ## 4. HITL 也是创新空间

            这里很适合做产品创新：

            - 哪些点该让人介入
            - 介入时展示什么信息
            - 怎么减少打断感
            - 怎么让确认更可理解
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **human-in-the-loop 不是失败补丁，而是系统设计的一部分。**
            2. **关键不在“要不要人工介入”，而在“在哪个点、以什么形式介入”。**
            3. **好的人机协作设计，能同时提升安全、效率和体验。**
            """
        ),
    ],
)

write_notebook(
    "mcp_21_agent_product_design.ipynb",
    [
        md(
            """
            # MCP 第 21 课：Agent Product Design，强系统不等于强产品

            走到这里，已经不能只用“模型强不强”来理解 agent 了。

            真正决定用户体验的，常常是产品设计问题：

            - 用户如何下达任务
            - 系统如何反馈进度
            - 失败如何解释
            - 工具权限如何表达
            """
        ),
        md(
            """
            ## 1. 产品视角和模型视角不一样

            模型视角会问：

            - 这个 prompt 怎么写
            - 这个 tool schema 怎么设计

            产品视角会问：

            - 用户为什么信任这个系统
            - 用户什么时候会中途放弃
            - 用户能不能理解系统刚才做了什么
            """
        ),
        md(
            """
            ## 2. 一个成熟 agent 产品通常要回答的 5 个问题

            - 它能做什么
            - 它不能做什么
            - 它正在做什么
            - 它为什么这么做
            - 它失败时怎么办
            """
        ),
        code(
            """
            product_questions = [
                "capability",
                "boundary",
                "progress",
                "reasoning summary",
                "failure recovery",
            ]

            product_questions
            """
        ),
        md(
            """
            ## 3. 真正重要的体验细节

            很多 agent 产品差距，来自这些小地方：

            - 任务输入方式是否自然
            - 中间进度是否清楚
            - 工具使用是否透明
            - 确认点是否合理
            - 最终报告是否能让人快速判断结果
            """
        ),
        md(
            """
            ## 4. 创新不只来自模型

            如果你未来想做创新，很值得看的方向包括：

            - 任务入口设计
            - 多轮协作体验
            - 批量任务体验
            - trace / diff / evidence 的呈现方式
            - 权限和确认的交互方式
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **agent 系统做得出来，不等于 agent 产品做得好用。**
            2. **产品设计会直接影响信任、效率和留存。**
            3. **创新很多时候发生在人机交互层，而不是只发生在模型层。**
            """
        ),
    ],
)

write_notebook(
    "mcp_22_failure_modes_and_debugging.ipynb",
    [
        md(
            """
            # MCP 第 22 课：Failure Modes 与 Debugging，Agent 出错时到底该怎么查

            复杂系统一定会出错。

            真正重要的不是“能不能完全不出错”，而是：

            **出错时你能不能快速定位、复现、修正。**
            """
        ),
        md(
            """
            ## 1. 先学会给失败分类

            一个实用分类法：

            - 理解失败：任务本身理解错了
            - 路由失败：选错工具或流程
            - 参数失败：参数格式或取值不对
            - 执行失败：工具或命令本身报错
            - 验证失败：结果没过测试或检查
            - 恢复失败：失败后没能调整策略
            """
        ),
        code(
            """
            failure_types = [
                "task misunderstanding",
                "wrong tool choice",
                "bad arguments",
                "execution error",
                "verification error",
                "recovery failure",
            ]

            failure_types
            """
        ),
        md(
            """
            ## 2. 调试顺序很重要

            出问题时，一个很稳的顺序通常是：

            1. 看 trace
            2. 看失败前最后一步
            3. 看输入和参数
            4. 看工具返回
            5. 看验证结果

            不要一上来就怪模型。
            """
        ),
        md(
            """
            ## 3. 为什么失败模式分析有创新价值

            很多团队只会说“模型不稳定”，但这太粗糙了。

            如果你能把失败模式系统化：

            - 你就能更快定位瓶颈
            - 你就能知道该改 prompt、工具还是工作流
            - 你就能更清楚地做产品迭代
            """
        ),
        md(
            """
            ## 4. 最值得保留的调试资产

            一个成熟团队通常会积累这些东西：

            - 失败案例库
            - 错误模式标签
            - 复盘模板
            - 回归测试样本
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **agent 调试的起点是分类失败，而不是笼统地说“不稳定”。**
            2. **trace、评估和失败案例库会一起构成你的调试能力。**
            3. **真正的工程进步，往往来自对失败的系统化理解。**
            """
        ),
    ],
)

write_notebook(
    "mcp_23_agent_innovation_map.ipynb",
    [
        md(
            """
            # MCP 第 23 课：Agent Innovation Map，未来到底还能在哪些地方创新

            到这里，你已经学了很多基础能力。

            最后这一课，我们不再只讲“怎么做”，而是专门回答：

            > 如果未来要做一个复杂 agent 项目，真正值得创新的地方在哪里？
            """
        ),
        md(
            """
            ## 1. 模型层创新

            这是大家最先想到的方向，但不是唯一方向。

            可能的创新点：

            - 更好的 routing
            - 更好的 step planning
            - 更好的 tool selection
            - 更强的 self-repair
            """
        ),
        md(
            """
            ## 2. 工具层创新

            这里往往被低估，但很值得做。

            例如：

            - 更稳定的工具 schema
            - 更强的错误回填
            - 更好的能力分层
            - 更安全的执行沙箱
            """
        ),
        md(
            """
            ## 3. 工作流层创新

            很多真正强的系统，强在 workflow，而不是单步能力。

            创新点包括：

            - 更合理的计划执行循环
            - 更好的验证闭环
            - 更高效的并行化
            - 更稳定的多代理协作
            """
        ),
        code(
            """
            innovation_layers = {
                "model": ["routing", "repair", "planning"],
                "tool": ["schema", "sandbox", "error feedback"],
                "workflow": ["verification", "parallelism", "handoffs"],
                "product": ["ux", "trust", "approval design"],
            }

            innovation_layers
            """
        ),
        md(
            """
            ## 4. 产品层创新

            很多爆款 agent 产品，并不是因为底层模型独家，而是因为：

            - 任务入口更自然
            - 进度反馈更清楚
            - 权限交互更舒服
            - 用户更愿意信任它
            """
        ),
        md(
            """
            ## 5. 基础设施层创新

            这类创新更“工程”，但壁垒往往更高：

            - tracing
            - evaluation
            - memory lifecycle
            - auditability
            - permission architecture
            """
        ),
        md(
            """
            ## 6. 最适合你的创新路径

            如果你已经把这些课程学完，我会建议你优先从这三类方向选一个：

            - 一个具体任务场景
            - 一个 workflow 瓶颈
            - 一个产品体验痛点

            不要一开始就想做“通用超级 agent”，那通常太散。
            """
        ),
        md(
            """
            ## 本课工程直觉

            1. **agent 创新绝不只发生在模型层。**
            2. **workflow、工具、安全、评估、产品体验，全都可能形成真正壁垒。**
            3. **越具体的问题，越容易长出真正有价值的创新。**
            """
        ),
    ],
)
