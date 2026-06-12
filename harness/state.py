"""Conversation state tracking for the agent harness."""
from __future__ import annotations

from typing import List, Optional

from common.models import AgentEvent, EventType, LLMMessage


class ConversationState:
    """Tracks messages and events for a single agent run."""

    def __init__(self, run_id: str, agent_id: str, task: str) -> None:
        self.run_id = run_id
        self.agent_id = agent_id
        self.task = task
        self.messages: List[LLMMessage] = []
        self.events: List[AgentEvent] = []

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(LLMMessage(role=role, content=content))

    def add_event(
        self,
        event_type: EventType,
        content: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        self.events.append(
            AgentEvent(
                run_id=self.run_id,
                type=event_type,
                content=content,
                metadata=metadata or {},
            )
        )
