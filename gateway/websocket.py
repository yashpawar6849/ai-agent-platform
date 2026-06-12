"""WebSocket routes for the agent gateway."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket

from common.models import AgentEvent
from gateway.dependencies import agents
from harness.llm import MockBackend
from harness.registry import ToolRegistry
from harness.runner import AgentRunner
from harness.tools.calculator_tool import calculator_tool_def
from harness.tools.code_tool import code_tool_def
from harness.tools.fetch_tool import fetch_tool_def
from harness.tools.file_tools import read_file_def, write_file_def
from harness.tools.math_tool import math_tool_def
from harness.tools.plot_tool import plot_tool_def
from harness.tools.shell_tool import shell_tool_def

router = APIRouter()


@router.websocket("/agents/{agent_id}/stream")
async def stream_agent(websocket: WebSocket, agent_id: str) -> None:
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        task: str = data.get("task", "")

        if agent_id not in agents:
            await websocket.send_json({"error": "Agent not found"})
            return

        agent = agents[agent_id]
        registry = ToolRegistry()
        for tool_name in agent.tools:
            if tool_name == "math_tool":
                registry.register(math_tool_def)
            elif tool_name == "code_tool":
                registry.register(code_tool_def)
            elif tool_name == "calculator_tool":
                registry.register(calculator_tool_def)
            elif tool_name == "fetch_tool":
                registry.register(fetch_tool_def)
            elif tool_name == "read_file":
                registry.register(read_file_def)
            elif tool_name == "write_file":
                registry.register(write_file_def)
            elif tool_name == "shell_tool":
                registry.register(shell_tool_def)
            elif tool_name == "plot_tool":
                registry.register(plot_tool_def)

        async def on_event(event: AgentEvent) -> None:
            await websocket.send_json(event.model_dump(mode="json"))

        runner = AgentRunner(registry, MockBackend())
        result = await runner.run(agent, task, event_callback=on_event)

        await websocket.send_json(
            {
                "type": "final",
                "result": result.result,
                "status": result.status.value,
            }
        )
    except Exception as exc:
        await websocket.send_json({"error": str(exc)})
    finally:
        await websocket.close()
