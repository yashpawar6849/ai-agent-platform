"""Tests for the agent gateway WebSocket streaming endpoint."""
import pytest
from fastapi.testclient import TestClient

from gateway.dependencies import agents, runs
from gateway.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_stores():
    agents.clear()
    runs.clear()


def test_websocket_stream():
    agent_req = {
        "name": "fib",
        "instruction": "Calculate and verify fibonacci",
        "tools": ["math_tool", "code_tool"],
        "llm_backend": "mock",
    }
    resp = client.post("/agents", json=agent_req)
    assert resp.status_code == 200
    agent = resp.json()

    with client.websocket_connect(f"/agents/{agent['id']}/stream") as ws:
        ws.send_json({"task": "Calculate fib(10) and verify with Python"})
        events = []
        while True:
            msg = ws.receive_json()
            if msg.get("type") == "final":
                assert "55" in msg.get("result", "")
                assert msg.get("status") == "completed"
                break
            if "error" in msg:
                pytest.fail(f"WebSocket error: {msg['error']}")
            events.append(msg)

    tool_calls = [e for e in events if e.get("type") == "tool_call"]
    tool_results = [e for e in events if e.get("type") == "tool_result"]
    assert len(tool_calls) == 2
    assert len(tool_results) == 2
