"""Agent runner: orchestrates the reasoning loop."""
from __future__ import annotations

from typing import Awaitable, Callable, Optional
from uuid import uuid4

from common.models import Agent, AgentEvent, EventType, RunResult, RunStatus
from harness.llm import LLMBackend
from harness.registry import ToolRegistry
from harness.state import ConversationState


class AgentRunner:
    """Runs an agent through the full execution loop."""

    def __init__(self, registry: ToolRegistry, llm: LLMBackend) -> None:
        self.registry = registry
        self.llm = llm

    async def run(
        self,
        agent: Agent,
        task: str,
        max_iterations: int = 10,
        event_callback: Optional[Callable[[AgentEvent], Awaitable[None]]] = None,
    ) -> RunResult:
        run_id = str(uuid4())
        state = ConversationState(
            run_id=run_id,
            agent_id=agent.id,
            task=task,
        )
        state.add_message("user", task)

        for iteration in range(max_iterations):
            response = await self.llm.generate(
                state.messages, self.registry.definitions()
            )

            if response.content:
                state.add_message("assistant", response.content)
                event = AgentEvent(
                    run_id=state.run_id,
                    type=EventType.MESSAGE,
                    content=response.content,
                    metadata={"iteration": iteration},
                )
                state.events.append(event)
                if event_callback:
                    await event_callback(event)

            if response.tool_calls:
                for tc in response.tool_calls:
                    call_event = AgentEvent(
                        run_id=state.run_id,
                        type=EventType.TOOL_CALL,
                        content=f"Calling {tc.name}",
                        metadata={
                            "tool": tc.name,
                            "args": tc.arguments,
                            "iteration": iteration,
                        },
                    )
                    state.events.append(call_event)
                    if event_callback:
                        await event_callback(call_event)

                    tool = self.registry.get(tc.name)
                    try:
                        result = await tool.execute(**tc.arguments)
                    except Exception as exc:
                        result = f"Error: {exc}"
                    state.add_message("tool", str(result))

                    result_event = AgentEvent(
                        run_id=state.run_id,
                        type=EventType.TOOL_RESULT,
                        content=str(result),
                        metadata={"tool": tc.name, "iteration": iteration},
                    )
                    state.events.append(result_event)
                    if event_callback:
                        await event_callback(result_event)
            else:
                final_event = AgentEvent(
                    run_id=state.run_id,
                    type=EventType.FINAL_ANSWER,
                    content=response.content or "",
                )
                state.events.append(final_event)
                if event_callback:
                    await event_callback(final_event)
                return RunResult(
                    run_id=state.run_id,
                    agent_id=agent.id,
                    task=task,
                    status=RunStatus.COMPLETED,
                    result=response.content,
                    events=state.events,
                )

        err_event = AgentEvent(
            run_id=state.run_id,
            type=EventType.ERROR,
            content="Max iterations reached without final answer",
        )
        state.events.append(err_event)
        if event_callback:
            await event_callback(err_event)
        return RunResult(
            run_id=state.run_id,
            agent_id=agent.id,
            task=task,
            status=RunStatus.COMPLETED,
            result="Max iterations reached",
            events=state.events,
        )
