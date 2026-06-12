"""Shared Pydantic models for the agent platform."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EventType(str, Enum):
    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    MESSAGE = "message"
    ERROR = "error"
    FINAL_ANSWER = "final_answer"


class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    instruction: str = "You are a helpful assistant."
    tools: List[str] = Field(default_factory=list)
    llm_backend: str = "mock"
    model: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class RunRequest(BaseModel):
    agent_id: str
    task: str
    max_iterations: int = 10
    timeout: int = 120


class AgentEvent(BaseModel):
    run_id: str
    type: EventType
    content: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)


class RunResult(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    task: str
    status: RunStatus = RunStatus.PENDING
    result: Optional[str] = None
    events: List[AgentEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: Optional[datetime] = None


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    finish_reason: Optional[str] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SandboxResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
