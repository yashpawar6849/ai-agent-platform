"""Shell command execution tool using Docker sandbox."""
from __future__ import annotations

from harness.registry import Tool
from sandbox.docker_sandbox import DockerSandbox


async def shell_tool(command: str) -> str:
    """Execute a shell command in a Docker sandbox and return stdout."""
    sandbox = DockerSandbox()
    result = await sandbox.run_command(
        ["sh", "-c", command],
        timeout=10,
        image="alpine:latest",
    )
    return result.stdout.strip()


shell_tool_def = Tool(
    name="shell_tool",
    description="Run a shell command inside an isolated Docker container.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
            },
        },
        "required": ["command"],
    },
    handler=shell_tool,
)