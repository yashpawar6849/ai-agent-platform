"""Tests for the SDK client and builder."""
from unittest.mock import MagicMock, patch

import pytest

from common.models import Agent, RunResult, RunStatus
from sdk import AgentBuilder, AgentClient


class TestAgentBuilder:
    def test_fluent_build(self):
        agent = (
            AgentBuilder()
            .name("fib_agent")
            .description("Computes fibonacci numbers")
            .instruction("Calculate fib(10) and verify with code.")
            .tool("math_tool")
            .tool("code_tool")
            .llm_backend("mock")
            .build()
        )
        assert agent.name == "fib_agent"
        assert agent.description == "Computes fibonacci numbers"
        assert agent.instruction == "Calculate fib(10) and verify with code."
        assert agent.tools == ["math_tool", "code_tool"]
        assert agent.llm_backend == "mock"

    def test_build_with_multiple_tools(self):
        agent = AgentBuilder().name("multi").tool("a").tool("b").tool("c").build()
        assert agent.tools == ["a", "b", "c"]

    def test_default_backend_is_mock(self):
        agent = AgentBuilder().name("test").build()
        assert agent.llm_backend == "mock"


class TestAgentClient:
    def test_create_agent(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "id": "agent-123",
            "name": "fib_agent",
            "instruction": "Calculate fibonacci numbers.",
            "tools": [],
            "llm_backend": "mock",
            "created_at": "2024-01-01T00:00:00Z",
        }
        mock_resp.raise_for_status.return_value = None

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.post.return_value = mock_resp
            client = AgentClient("http://localhost:8000")
            agent = Agent(name="fib_agent", instruction="Calculate fibonacci numbers.")
            created = client.create_agent(agent)

        assert created.id == "agent-123"
        assert created.name == "fib_agent"
        assert created.llm_backend == "mock"

    def test_run_task(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "run_id": "run-456",
            "agent_id": "agent-123",
            "task": "Calculate fib(10)",
            "status": "completed",
            "result": "55",
            "events": [],
            "created_at": "2024-01-01T00:00:00Z",
        }
        mock_resp.raise_for_status.return_value = None

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.post.return_value = mock_resp
            client = AgentClient("http://localhost:8000")
            result = client.run_task("agent-123", "Calculate fib(10)")

        assert result.run_id == "run-456"
        assert result.status == RunStatus.COMPLETED
        assert result.result == "55"
        assert result.agent_id == "agent-123"

    def test_context_manager(self):
        with patch("httpx.Client") as MockClient:
            with AgentClient("http://localhost:8000") as client:
                assert isinstance(client, AgentClient)
            MockClient.return_value.close.assert_called_once()
