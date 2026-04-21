from __future__ import annotations

import sys
from datetime import date, datetime

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("MCP Course Demo Server", json_response=True)


COURSE_OUTLINE = """
MCP 课程路线图：
1. 理解 MCP 是什么，为什么需要标准协议
2. 学会区分 tools / resources / prompts
3. 用 client 连接 server，理解 initialize / list / call 流程
4. 手写一个真正可运行的 MCP server
5. 让本地 LLM 通过 MCP 使用外部能力
""".strip()


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@mcp.tool()
def days_between(start_date: str, end_date: str) -> int:
    """Return the day difference between two ISO dates like 2026-04-20."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    return (end - start).days


@mcp.tool()
def summarize_learning_goal(topic: str, level: str = "beginner") -> str:
    """Generate a compact study goal for a topic."""
    return (
        f"For a {level} learner, focus on the core mental model of {topic}, "
        f"one runnable example, and one debugging checklist."
    )


@mcp.resource("course://outline")
def get_course_outline() -> str:
    """Read the course outline."""
    return COURSE_OUTLINE


@mcp.resource("date://today")
def get_today() -> str:
    """Read today's date from the server."""
    return date.today().isoformat()


@mcp.resource("student://{name}")
def get_student_note(name: str) -> str:
    """Return a personalized note for a student."""
    return (
        f"Hi {name}, MCP is easiest when you treat it as a standard contract "
        f"between an LLM app and outside capabilities."
    )


@mcp.prompt()
def explain_mcp(topic: str, audience: str = "beginner") -> str:
    """Build a reusable teaching prompt about MCP."""
    return (
        f"Please explain {topic} in Chinese for a {audience}. "
        f"Use one analogy, one concrete example, and end with a short checklist."
    )


@mcp.prompt()
def build_exercise(topic: str, difficulty: str = "easy") -> str:
    """Build a small exercise prompt."""
    return (
        f"Create one {difficulty} hands-on exercise about {topic}. "
        f"Include the goal, starter code idea, and what success looks like."
    )


if __name__ == "__main__":
    print(
        f"[{datetime.now().isoformat()}] Starting MCP Course Demo Server on stdio",
        file=sys.stderr,
    )
    mcp.run()
