"""Integration tests across the full stack."""
import pytest
from fastapi.testclient import TestClient

from gateway.dependencies import agents, runs
from gateway.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_stores():
    agents.clear()
    runs.clear()


def test_full_integration():
    agent_req = {
        "name": "fib",
        "instruction": "Calculate and verify fibonacci",
        "tools": ["math_tool", "code_tool"],
        "llm_backend": "mock",
    }
    resp = client.post("/agents", json=agent_req)
    assert resp.status_code == 200
    agent = resp.json()

    run_req = {
        "agent_id": agent["id"],
        "task": "Calculate fib(10) and verify with Python",
        "max_iterations": 10,
        "timeout": 120,
    }
    resp = client.post(f"/agents/{agent['id']}/run", json=run_req)
    assert resp.status_code == 200
    result = resp.json()
    assert result["status"] == "completed"
    assert "55" in result["result"]

    events = result["events"]
    tool_calls = [e for e in events if e["type"] == "tool_call"]
    tool_results = [e for e in events if e["type"] == "tool_result"]
    assert len(tool_calls) == 2
    assert tool_calls[0]["metadata"]["tool"] == "math_tool"
    assert tool_calls[1]["metadata"]["tool"] == "code_tool"
    assert len(tool_results) == 2
