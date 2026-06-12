"""SDK client for the agent platform gateway."""
from __future__ import annotations

import httpx

from common.models import Agent, RunRequest, RunResult


class AgentClient:
    """Synchronous HTTP client for the agent gateway."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 120.0):
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self._base_url, timeout=timeout)

    def create_agent(self, agent: Agent) -> Agent:
        """Create a new agent via the gateway."""
        resp = self._client.post("/agents", json=agent.model_dump(mode="json"))
        resp.raise_for_status()
        return Agent.model_validate(resp.json())

    def run_task(
        self,
        agent_id: str,
        task: str,
        max_iterations: int = 10,
        timeout: int = 120,
    ) -> RunResult:
        """Submit a task to an agent and return the run result."""
        req = RunRequest(
            agent_id=agent_id,
            task=task,
            max_iterations=max_iterations,
            timeout=timeout,
        )
        resp = self._client.post(
            f"/agents/{agent_id}/run",
            json=req.model_dump(mode="json"),
        )
        resp.raise_for_status()
        return RunResult.model_validate(resp.json())

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AgentClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
