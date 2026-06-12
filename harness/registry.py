"""Tool registry for the agent harness."""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List

from common.models import ToolDefinition


class Tool:
    """Represents a tool available to agents."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Awaitable[Any]],
    ) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )

    async def execute(self, **kwargs: Any) -> Any:
        return await self.handler(**kwargs)


class ToolRegistry:
    """Registry for discovering and dispatching tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def definitions(self) -> List[ToolDefinition]:
        return [t.definition for t in self._tools.values()]
