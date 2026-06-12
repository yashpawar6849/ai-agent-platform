"""Fluent builder for Agent configuration."""
from __future__ import annotations

from typing import List, Optional

from common.models import Agent


class AgentBuilder:
    """Fluent builder for constructing Agent instances."""

    def __init__(self):
        self._name: str = "unnamed"
        self._description: Optional[str] = None
        self._instruction: str = "You are a helpful assistant."
        self._tools: List[str] = []
        self._llm_backend: str = "mock"
        self._model: Optional[str] = None

    def name(self, value: str) -> AgentBuilder:
        self._name = value
        return self

    def description(self, value: str) -> AgentBuilder:
        self._description = value
        return self

    def instruction(self, value: str) -> AgentBuilder:
        self._instruction = value
        return self

    def tool(self, value: str) -> AgentBuilder:
        self._tools.append(value)
        return self

    def llm_backend(self, value: str) -> AgentBuilder:
        self._llm_backend = value
        return self

    def model(self, value: str) -> AgentBuilder:
        self._model = value
        return self

    def build(self) -> Agent:
        return Agent(
            name=self._name,
            description=self._description,
            instruction=self._instruction,
            tools=self._tools.copy(),
            llm_backend=self._llm_backend,
            model=self._model,
        )
