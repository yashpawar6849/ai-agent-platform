"""Fetch tool: HTTP GET requests with size limit."""
from __future__ import annotations

import httpx
from harness.registry import Tool


async def fetch_tool(url: str) -> str:
    """Fetch content from a URL.

    Args:
        url: The URL to fetch via GET request.

    Returns:
        The first 5000 characters of the response, or an error message.
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text[:5000]
    except Exception as exc:
        return f"Error: {exc}"


fetch_tool_def = Tool(
    name="fetch_tool",
    description="Fetch the content of a URL via HTTP GET request.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to fetch",
            },
        },
        "required": ["url"],
    },
    handler=fetch_tool,
)