"""Structured Observability, Telemetry, Intent Logging, and PII Data Scrubbing for EduPathway AI."""

import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..models.trace import SessionTrace, AgentTrace, ToolExecutionTrace, TraceEvent, EventType
from ..config import config


class PIIScrubber:
    """Enterprise-grade PII redaction and sensitive data sanitizer for student profiles."""

    # Common PII Regex Patterns
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    
    # Specific Student Identifiers to Sanitize
    KNOWN_NAMES = ["Leo Martinez", "Leo", "Martinez", "Jane Doe", "John Doe"]

    @classmethod
    def scrub_text(cls, text: str) -> str:
        """Sanitize text by redacting emails, phone numbers, SSNs, and known student names."""
        if not isinstance(text, str):
            return str(text)

        sanitized = text
        sanitized = cls.EMAIL_PATTERN.sub("[EMAIL_REDACTED]", sanitized)
        sanitized = cls.PHONE_PATTERN.sub("[PHONE_REDACTED]", sanitized)
        sanitized = cls.SSN_PATTERN.sub("[SSN_REDACTED]", sanitized)

        for name in cls.KNOWN_NAMES:
            sanitized = re.sub(rf"\b{re.escape(name)}\b", "[STUDENT_NAME_REDACTED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    @classmethod
    def scrub_data(cls, data: Any) -> Any:
        """Recursively scrub dictionaries, lists, and primitives of PII."""
        if isinstance(data, dict):
            return {cls.scrub_text(str(k)): cls.scrub_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.scrub_data(item) for item in data]
        elif isinstance(data, str):
            return cls.scrub_text(data)
        elif isinstance(data, (int, float, bool)) or data is None:
            return data
        else:
            return cls.scrub_text(str(data))


class Tracer:
    """Central event collector, telemetry recorder, intent logger, and structured trace exporter."""

    def __init__(self, session_id: str, student_id: str, enable_pii_redaction: bool = True):
        self.enable_pii_redaction = enable_pii_redaction
        scrubbed_student_id = PIIScrubber.scrub_text(student_id) if enable_pii_redaction else student_id
        
        self.session_trace = SessionTrace(
            session_id=session_id,
            student_id=scrubbed_student_id,
            start_time=datetime.utcnow(),
        )
        self._start_time_perf = time.perf_counter()
        os.makedirs(config.traces_dir, exist_ok=True)
        
        self.emit_event(
            EventType.SESSION_START,
            {"student_id": scrubbed_student_id, "pii_redaction_active": enable_pii_redaction}
        )

    def record_intent(
        self,
        agent_name: str,
        intent: str,
        planned_tools: Optional[List[str]] = None,
        expected_outcome: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TraceEvent:
        """Record explicit pre-execution intent before agent or tool invocation (Intent vs. Outcome)."""
        payload = {
            "intent": intent,
            "planned_tools": planned_tools or [],
            "expected_outcome": expected_outcome or "Successful pedagogical execution",
            "context": context or {},
        }
        if self.enable_pii_redaction:
            payload = PIIScrubber.scrub_data(payload)

        return self.emit_event(
            EventType.INTENT_DECLARED,
            payload=payload,
            agent_name=agent_name,
        )

    def emit_event(
        self,
        event_type: EventType,
        payload: Optional[Dict[str, Any]] = None,
        agent_name: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> TraceEvent:
        """Emit a timestamped timeline trace event with automated PII scrubbing."""
        event_id = f"evt_{len(self.session_trace.events) + 1:04d}"
        clean_payload = PIIScrubber.scrub_data(payload or {}) if self.enable_pii_redaction else (payload or {})
        
        event = TraceEvent(
            event_id=event_id,
            session_id=self.session_trace.session_id,
            event_type=event_type,
            agent_name=agent_name,
            payload=clean_payload,
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
        """Record a completed tool execution with latency, input/output validation, and PII scrubbing."""
        clean_inputs = PIIScrubber.scrub_data(inputs) if self.enable_pii_redaction else inputs
        clean_output = PIIScrubber.scrub_data(output) if self.enable_pii_redaction else output

        tool_trace = ToolExecutionTrace(
            tool_name=tool_name,
            inputs=clean_inputs,
            output=clean_output,
            duration_ms=round(duration_ms, 2),
            success=success,
            error_message=error_message,
            timestamp=datetime.utcnow(),
        )
        self.session_trace.total_tool_calls += 1

        # Emit tool outcome event
        evt_type = EventType.TOOL_END if success else EventType.TOOL_ERROR
        self.emit_event(
            evt_type,
            {
                "tool_name": tool_name,
                "inputs": clean_inputs,
                "output_preview": str(clean_output)[:200] if clean_output else None,
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
        """Record an agent's execution lifecycle and token consumption."""
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
        """Export full scrubbed JSON trace file to traces directory."""
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
