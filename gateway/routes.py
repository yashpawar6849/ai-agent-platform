"""REST routes for the agent gateway."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from common.models import Agent, RunRequest, RunResult, RunStatus
from gateway.dependencies import agents, runs
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


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/agents", response_model=Agent)
async def create_agent(agent: Agent) -> Agent:
    agents[agent.id] = agent
    return agent


@router.post("/agents/{agent_id}/run", response_model=RunResult)
async def run_task(agent_id: str, req: RunRequest) -> RunResult:
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

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

    runner = AgentRunner(registry, MockBackend())
    result = await runner.run(
        agent, req.task, max_iterations=req.max_iterations
    )
    runs[result.run_id] = result
    return result


@router.get("/agents/{agent_id}/runs/{run_id}", response_model=RunResult)
async def get_run(agent_id: str, run_id: str) -> RunResult:
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return runs[run_id]
