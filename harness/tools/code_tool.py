"""Sandboxed code execution tool."""
from __future__ import annotations

from harness.registry import Tool
from sandbox.docker_sandbox import DockerSandbox


async def code_tool(code: str) -> str:
    """Execute Python code in a Docker sandbox and return stdout."""
    sandbox = DockerSandbox()
    result = await sandbox.run_code(code, timeout=10)
    return result.stdout.strip()


code_tool_def = Tool(
    name="code_tool",
    description="Execute Python code in a sandboxed Docker container and return stdout.",
    parameters={
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python source code to execute",
            },
        },
        "required": ["code"],
    },
    handler=code_tool,
)
