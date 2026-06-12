"""LLM backend abstraction with mock and OpenAI-compatible implementations."""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import List

from common.models import LLMMessage, LLMResponse, ToolCall, ToolDefinition


class LLMBackend(ABC):
    """Abstract LLM backend for the agent harness."""

    @abstractmethod
    async def generate(
        self, messages: List[LLMMessage], tools: List[ToolDefinition]
    ) -> LLMResponse:
        ...


class MockBackend(LLMBackend):
    """Deterministic mock backend that simulates the Fibonacci demo.

    Step 1: calls math_tool(n=10)
    Step 2: calls code_tool with a short fibonacci script (if available)
    Step 3: returns final answer containing 55
    """

    async def generate(
        self, messages: List[LLMMessage], tools: List[ToolDefinition]
    ) -> LLMResponse:
        tool_results = [m for m in messages if m.role == "tool"]
        iteration = len(tool_results)
        available = {t.name for t in tools}

        if iteration == 0:
            return LLMResponse(
                content=None,
                tool_calls=[ToolCall(name="math_tool", arguments={"n": 10})],
            )
        if iteration == 1 and "code_tool" in available:
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        name="code_tool",
                        arguments={
                            "code": (
                                "def fib(n):\n"
                                "    if n < 2:\n"
                                "        return n\n"
                                "    return fib(n-1) + fib(n-2)\n"
                                "print(fib(10))"
                            )
                        },
                    )
                ],
            )
        return LLMResponse(
            content="The 10th Fibonacci number is 55.",
            tool_calls=[],
        )


class OpenAIBackend(LLMBackend):
    """OpenAI-compatible backend (GPT-4, etc.)."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "OpenAI backend requires the 'openai' package. "
                "Install it with: pip install openai"
            ) from exc
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self._client = openai.AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self, messages: List[LLMMessage], tools: List[ToolDefinition]
    ) -> LLMResponse:
        openai_messages = [
            {"role": m.role, "content": m.content} for m in messages
        ]
        openai_tools = None
        if tools:
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ]

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=openai_tools,
            tool_choice="auto" if openai_tools else None,
        )

        choice = response.choices[0]
        message = choice.message

        tool_calls: List[ToolCall] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
        )
