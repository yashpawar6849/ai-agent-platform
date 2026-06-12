"""Safe math tool: calculates Fibonacci numbers."""
from __future__ import annotations

from harness.registry import Tool


async def math_tool(n: int) -> int:
    """Calculate the nth Fibonacci number."""

    def _fib(k: int) -> int:
        if k < 2:
            return k
        return _fib(k - 1) + _fib(k - 2)

    return _fib(n)


math_tool_def = Tool(
    name="math_tool",
    description="Calculate the nth Fibonacci number recursively.",
    parameters={
        "type": "object",
        "properties": {
            "n": {
                "type": "integer",
                "description": "Index in the Fibonacci sequence (0-based)",
            },
        },
        "required": ["n"],
    },
    handler=math_tool,
)
