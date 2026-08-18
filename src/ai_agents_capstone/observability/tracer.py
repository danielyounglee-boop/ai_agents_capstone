"""Structured Observability, Telemetry, and Execution Tracer for EduPathway AI."""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional
from ..models.trace import SessionTrace, AgentTrace, ToolExecutionTrace, TraceEvent, EventType
from ..config import config


class Tracer:
    """Central event collector, telemetry recorder, and structured trace exporter."""

    def __init__(self, session_id: str, student_id: str):
        self.session_trace = SessionTrace(
            session_id=session_id,
            student_id=student_id,
            start_time=datetime.utcnow(),
        )
        self._start_time_perf = time.perf_counter()
        os.makedirs(config.traces_dir, exist_ok=True)
        self.emit_event(EventType.SESSION_START, {"student_id": student_id})

    def emit_event(
        self,
        event_type: EventType,
        payload: Optional[Dict[str, Any]] = None,
        agent_name: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> TraceEvent:
        """Emit a timestamped timeline trace event."""
        event_id = f"evt_{len(self.session_trace.events) + 1:04d}"
        event = TraceEvent(
            event_id=event_id,
            session_id=self.session_trace.session_id,
            event_type=event_type,
            agent_name=agent_name,
            payload=payload or {},
            duration_ms=duration_ms,
            timestamp=datetime.utcnow(),
        )
        self.session_trace.events.append(event)
        return event

    def record_tool_call(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
        output: Any,
        duration_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> ToolExecutionTrace:
        """Record a completed tool execution with latency and status."""
        tool_trace = ToolExecutionTrace(
            tool_name=tool_name,
            inputs=inputs,
            output=output,
            duration_ms=round(duration_ms, 2),
            success=success,
            error_message=error_message,
            timestamp=datetime.utcnow(),
        )
        self.session_trace.total_tool_calls += 1

        # Emit tool event
        evt_type = EventType.TOOL_END if success else EventType.TOOL_ERROR
        self.emit_event(
            evt_type,
            {
                "tool_name": tool_name,
                "inputs": inputs,
                "output_preview": str(output)[:200] if output else None,
                "duration_ms": duration_ms,
                "success": success,
                "error": error_message,
            },
            agent_name=agent_name,
            duration_ms=duration_ms,
        )
        return tool_trace

    def record_agent_invocation(
        self,
        agent_name: str,
        model_name: str,
        duration_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        tool_traces: Optional[list] = None,
        state_in: Optional[str] = None,
        state_out: Optional[str] = None,
    ) -> AgentTrace:
        """Record an agent's execution lifecycle."""
        total_tokens = prompt_tokens + completion_tokens
        agent_trace = AgentTrace(
            agent_name=agent_name,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            duration_ms=round(duration_ms, 2),
            tool_calls=tool_traces or [],
            state_in=state_in,
            state_out=state_out,
        )
        self.session_trace.agent_traces.append(agent_trace)
        self.session_trace.total_tokens_consumed += total_tokens

        self.emit_event(
            EventType.AGENT_END,
            {
                "agent_name": agent_name,
                "model": model_name,
                "total_tokens": total_tokens,
                "duration_ms": duration_ms,
                "state_out": state_out,
            },
            agent_name=agent_name,
            duration_ms=duration_ms,
        )
        return agent_trace

    def record_hitl(self, triggered: bool, reason: str, decision: str, notes: Optional[str] = None) -> None:
        """Record a Human-in-the-Loop review event."""
        evt_type = EventType.HITL_TRIGGERED if triggered else EventType.HITL_RESOLVED
        self.emit_event(
            evt_type,
            {
                "triggered": triggered,
                "reason": reason,
                "decision": decision,
                "notes": notes,
            },
        )

    def record_state_transition(self, from_state: str, to_state: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Record an orchestration state machine transition."""
        self.emit_event(
            EventType.STATE_TRANSITION,
            {
                "from_state": from_state,
                "to_state": to_state,
                "details": details or {},
            },
        )

    def finish_session(self) -> SessionTrace:
        """Finalize the session trace and calculate total session metrics."""
        elapsed_sec = time.perf_counter() - self._start_time_perf
        self.session_trace.end_time = datetime.utcnow()
        self.session_trace.total_duration_ms = round(elapsed_sec * 1000, 2)
        self.emit_event(EventType.SESSION_END, {"total_duration_ms": self.session_trace.total_duration_ms})
        self.export_trace()
        return self.session_trace

    def export_trace(self, custom_path: Optional[str] = None) -> str:
        """Export full JSON trace file to traces directory."""
        file_path = custom_path or os.path.join(config.traces_dir, f"trace_{self.session_trace.session_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.session_trace.model_dump_json(indent=2))
        return os.path.abspath(file_path)

    def get_summary_report(self) -> str:
        """Generate human-readable execution and observability metrics."""
        st = self.session_trace
        lines = [
            "============================================================",
            f"📊 OBSERVABILITY TRACE SUMMARY (Session: {st.session_id})",
            "============================================================",
            f"• Student ID:            {st.student_id}",
            f"• Total Duration:        {st.total_duration_ms:.1f} ms",
            f"• Total Tool Calls:      {st.total_tool_calls}",
            f"• Total Tokens Consumed: {st.total_tokens_consumed}",
            f"• Agent Invocations:     {len(st.agent_traces)}",
            f"• Recorded Trace Events: {len(st.events)}",
            "------------------------------------------------------------",
            "Agent Breakdown:",
        ]
        for at in st.agent_traces:
            lines.append(
                f"  - [{at.agent_name}] Model: {at.model_name} | Latency: {at.duration_ms:.1f}ms | Tokens: {at.total_tokens} | Tools: {len(at.tool_calls)}"
            )
        lines.append("============================================================")
        return "\n".join(lines)
