"""Tests for the agent harness."""
import pytest

from common.models import Agent, EventType, RunStatus
from harness import AgentRunner, MockBackend, ToolRegistry
from harness.tools.math_tool import math_tool_def


@pytest.mark.asyncio
async def test_math_tool():
    registry = ToolRegistry()
    registry.register(math_tool_def)
    runner = AgentRunner(registry, MockBackend())
    agent = Agent(name="fib", instruction="Calculate fibonacci")
    result = await runner.run(agent, "Calculate fib(10)")
    assert result.status == RunStatus.COMPLETED
    assert "55" in result.result
    assert any(e.type == EventType.TOOL_CALL for e in result.events)
    assert any(e.type == EventType.TOOL_RESULT for e in result.events)


@pytest.mark.asyncio
async def test_mock_agent_loop_completes():
    registry = ToolRegistry()
    registry.register(math_tool_def)
    runner = AgentRunner(registry, MockBackend())
    agent = Agent(name="fib", instruction="Calculate fibonacci")
    result = await runner.run(agent, "Calculate fib(10)")
    assert result.result == "The 10th Fibonacci number is 55."
    tool_calls = [e for e in result.events if e.type == EventType.TOOL_CALL]
    assert len(tool_calls) == 1
    assert tool_calls[0].metadata["tool"] == "math_tool"
