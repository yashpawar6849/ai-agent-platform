"""Matplotlib plot generation tool."""
from __future__ import annotations

import base64
import io
import tempfile
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from harness.registry import Tool

matplotlib.use("Agg")


async def plot_tool(expression: str, title: str = "Plot") -> str:
    """Generate a matplotlib plot from a numpy expression and return as base64 PNG."""
    try:
        x = np.linspace(-10, 10, 400)
        y = eval(expression, {"__builtins__": {}}, {"np": np, "x": x})

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y)
        ax.set_title(title)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100)
        buf.seek(0)
        png_data = buf.read()
        plt.close(fig)

        b64 = base64.b64encode(png_data).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception as exc:
        return f"Error: {exc}"


plot_tool_def = Tool(
    name="plot_tool",
    description="Generate a matplotlib plot from a numpy expression (e.g., np.sin(x)) and return as base64 PNG.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Python numpy expression for y(x). Use np for numpy, x for the input array.",
            },
            "title": {
                "type": "string",
                "description": "Plot title",
            },
        },
        "required": ["expression"],
    },
    handler=plot_tool,
)
