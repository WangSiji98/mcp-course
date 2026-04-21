# MCP 教程

这套课程仿照 `agent-course-notebooks` 的风格来写：少量概念、清晰的图景、可直接运行的代码。

课程目标：

- 理解 MCP 是什么，以及它和普通 API / tool calling 的关系
- 理解 MCP 的核心原语：`tools`、`resources`、`prompts`、`transport`
- 学会用 Python 写一个最小 MCP client
- 从零写出一个真正可运行的 MCP server
- 把本地 LM Studio 的 OpenAI 兼容接口接进来，让 LLM 能通过 MCP 使用工具

课程文件：

- `mcp_01_what_is_mcp.ipynb`
- `mcp_02_mcp_primitives.ipynb`
- `mcp_03_mcp_client.ipynb`
- `mcp_04_build_mcp_server.ipynb`
- `mcp_05_llm_with_mcp.ipynb`

配套代码：

- `src/mcp_course/server.py`：最终版 MCP server
- `src/mcp_course/client_minimal.py`：最小 MCP client
- `src/mcp_course/llm_bridge.py`：把本地 OpenAI 兼容 LLM 和 MCP server 串起来
- `scripts/generate_notebooks.py`：生成课程 notebook

## 运行环境

本目录配套的 conda 环境名是 `mcp`。

激活环境：

```bash
conda activate mcp
```

如果你想在 Jupyter 中使用它，kernel 名称是 `Python (mcp)`。

## 配置本地 LLM

课程默认使用 LM Studio 暴露的 OpenAI 兼容接口：

- Base URL: `http://10.0.0.63:1234/v1`
- API Key: `lm-studio`

你可以复制 `.env.example` 为 `.env`，再按需改模型名。

## 快速开始

启动 MCP server：

```bash
conda run -n mcp python /Users/siji/Desktop/AI/mcp/src/mcp_course/server.py
```

运行最小 client：

```bash
conda run -n mcp python /Users/siji/Desktop/AI/mcp/src/mcp_course/client_minimal.py
```

运行 LLM + MCP bridge：

```bash
conda run -n mcp python /Users/siji/Desktop/AI/mcp/src/mcp_course/llm_bridge.py
```

## 参考

本课程实现主要参考官方 MCP 文档与 Python SDK：

- https://modelcontextprotocol.io/docs/sdk
- https://py.sdk.modelcontextprotocol.io/
- https://github.com/modelcontextprotocol/python-sdk
