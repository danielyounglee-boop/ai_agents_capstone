"""Unit tests for observability, intent logging, and PII data scrubbing."""

import json
import os
import pytest
from src.ai_agents_capstone.observability.tracer import Tracer, PIIScrubber
from src.ai_agents_capstone.models.trace import EventType


def test_cloud_dlp_scrubber():
    """Verify that Google Cloud DLP de-identification engine sanitizes PII."""
    from src.ai_agents_capstone.observability.dlp_scrubber import CloudDLPScrubber
    
    dlp = CloudDLPScrubber()
    sample_text = "Student Leo Martinez reached out from leo.m@school.edu."
    scrubbed = dlp.deidentify_text(sample_text)
    
    assert "Leo Martinez" not in scrubbed
    assert "leo.m@school.edu" not in scrubbed
    assert "[STUDENT_NAME_REDACTED]" in scrubbed
    assert "[EMAIL_REDACTED]" in scrubbed


def test_tracer_lifecycle(tmp_path):
    """Verify trace lifecycle, intent-before-outcome logging, and export."""
    tracer = Tracer(session_id="test_obs_sess", student_id="Leo Martinez", enable_pii_redaction=True)
    
    # Record intent before execution
    intent_evt = tracer.record_intent(
        agent_name="IntakeAssessmentAgent",
        intent="Analyze student misconceptions on fractions.",
        planned_tools=["analyze_readability"],
        expected_outcome="Accurate Diagnostic Report",
    )
    assert intent_evt.event_type == EventType.INTENT_DECLARED

    tracer.record_tool_call(
        tool_name="analyze_readability",
        inputs={"text": "Leo Martinez says fraction addition is tricky."},
        output={"fk_grade": 1.0, "status": "success"},
        duration_ms=12.5,
        success=True,
    )
    tracer.record_agent_invocation(
        agent_name="IntakeAssessmentAgent",
        model_name="gemini-2.5-flash",
        duration_ms=250.0,
        prompt_tokens=100,
        completion_tokens=50,
    )
    tracer.record_state_transition("INIT", "DIAGNOSIS")
    trace = tracer.finish_session()

    assert trace.session_id == "test_obs_sess"
    assert trace.student_id == "[STUDENT_NAME_REDACTED]"
    assert trace.total_tool_calls == 1
    assert trace.total_tokens_consumed == 150
    assert len(trace.events) >= 4

    # Check exported JSON trace contains scrubbed PII
    export_file = tmp_path / "test_trace.json"
    exported_path = tracer.export_trace(str(export_file))
    assert os.path.exists(exported_path)

    with open(exported_path, "r", encoding="utf-8") as f:
        trace_json = json.load(f)
    assert "Leo Martinez" not in json.dumps(trace_json)

    summary = tracer.get_summary_report()
    assert "OBSERVABILITY TRACE SUMMARY" in summary
    assert "IntakeAssessmentAgent" in summary
