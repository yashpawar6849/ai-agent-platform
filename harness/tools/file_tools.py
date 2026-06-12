"""File tools: sandboxed read/write within a restricted directory."""
from __future__ import annotations

import os
from pathlib import Path

from harness.registry import Tool

SANDBOX_ROOT = Path("/tmp/agent_sandbox")


def _resolve_and_validate(path: str) -> Path:
    """Resolve a path and validate it's within the sandbox."""
    resolved = (SANDBOX_ROOT / path).resolve()
    if not str(resolved).startswith(str(SANDBOX_ROOT)):
        raise ValueError("Path traversal detected")
    return resolved


async def read_file(path: str) -> str:
    """Read a file from within the sandbox.

    Args:
        path: Relative path within the sandbox.

    Returns:
        The file contents, or an error message if reading fails.
    """
    try:
        resolved = _resolve_and_validate(path)
        return resolved.read_text()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except ValueError as exc:
        return f"Error: {exc}"
    except Exception as exc:
        return f"Error: {exc}"


async def write_file(path: str, content: str) -> str:
    """Write content to a file within the sandbox.

    Args:
        path: Relative path within the sandbox.
        content: The content to write.

    Returns:
        A success message or error message.
    """
    try:
        resolved = _resolve_and_validate(path)
        # Ensure parent directory exists
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except ValueError as exc:
        return f"Error: {exc}"
    except Exception as exc:
        return f"Error: {exc}"


# Ensure sandbox root exists
SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)

read_file_def = Tool(
    name="read_file",
    description="Read a file from within the sandbox directory.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path within the sandbox.",
            },
        },
        "required": ["path"],
    },
    handler=read_file,
)

write_file_def = Tool(
    name="write_file",
    description="Write content to a file within the sandbox directory.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path within the sandbox.",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file.",
            },
        },
        "required": ["path", "content"],
    },
    handler=write_file,
)