"""Tests for the agent gateway REST endpoints."""
import pytest
from fastapi.testclient import TestClient

from gateway.dependencies import agents, runs
from gateway.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_stores():
    agents.clear()
    runs.clear()


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_agent_and_run():
    agent_req = {
        "name": "fib",
        "instruction": "Calculate fibonacci",
        "tools": ["math_tool"],
        "llm_backend": "mock",
    }
    resp = client.post("/agents", json=agent_req)
    assert resp.status_code == 200
    agent = resp.json()

    run_req = {
        "agent_id": agent["id"],
        "task": "Calculate fib(10)",
        "max_iterations": 10,
        "timeout": 120,
    }
    resp = client.post(f"/agents/{agent['id']}/run", json=run_req)
    assert resp.status_code == 200
    result = resp.json()
    assert result["status"] == "completed"
    assert "55" in result["result"]

    # Poll for run details
    run_id = result["run_id"]
    resp = client.get(f"/agents/{agent['id']}/runs/{run_id}")
    assert resp.status_code == 200
    polled = resp.json()
    assert polled["run_id"] == run_id
    assert "events" in polled
