"""Telemetry, event logging, and observability schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of telemetry events emitted across the multi-agent pipeline."""

    INTENT_DECLARED = "INTENT_DECLARED"
    SESSION_START = "SESSION_START"
    SESSION_END = "SESSION_END"
    AGENT_START = "AGENT_START"
    AGENT_END = "AGENT_END"
    TOOL_START = "TOOL_START"
    TOOL_END = "TOOL_END"
    TOOL_ERROR = "TOOL_ERROR"
    HITL_TRIGGERED = "HITL_TRIGGERED"
    HITL_RESOLVED = "HITL_RESOLVED"
    STATE_TRANSITION = "STATE_TRANSITION"
    MEMORY_UPDATE = "MEMORY_UPDATE"
    DATA_SCRUBBED = "DATA_SCRUBBED"


class ToolExecutionTrace(BaseModel):
    """Execution telemetry for a single tool call."""

    tool_name: str
    inputs: Dict[str, Any]
    output: Optional[Any] = None
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentTrace(BaseModel):
    """Trace for an individual agent invocation."""

    agent_name: str
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_ms: float = 0.0
    tool_calls: List[ToolExecutionTrace] = Field(default_factory=list)
    state_in: Optional[str] = None
    state_out: Optional[str] = None


class TraceEvent(BaseModel):
    """Individual atomic timeline trace event."""

    event_id: str
    session_id: str
    event_type: EventType
    agent_name: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionTrace(BaseModel):
    """Complete audit and observability trace for a full workflow execution."""

    session_id: str
    student_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    total_tokens_consumed: int = 0
    total_tool_calls: int = 0
    events: List[TraceEvent] = Field(default_factory=list)
    agent_traces: List[AgentTrace] = Field(default_factory=list)
