"""Calculator tool: safe mathematical expression evaluation."""
from __future__ import annotations

import math
from harness.registry import Tool

SAFE_MATH = {
    "abs": abs,
    "round": round,
    "pow": pow,
    "sqrt": math.sqrt,
    "log": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
    "e": math.e,
    "floor": math.floor,
    "ceil": math.ceil,
}


async def calculator_tool(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression using safe functions.

    Returns:
        The result as a string, or an error message if evaluation fails.
    """
    try:
        result = eval(expression, {"__builtins__": None}, SAFE_MATH)
        return str(result)
    except Exception as exc:
        return f"Error: {exc}"


calculator_tool_def = Tool(
    name="calculator_tool",
    description="Evaluate a mathematical expression safely using basic arithmetic and math functions.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A mathematical expression using safe functions (abs, round, pow, sqrt, log, sin, cos, tan, floor, ceil).",
            },
        },
        "required": ["expression"],
    },
    handler=calculator_tool,
)