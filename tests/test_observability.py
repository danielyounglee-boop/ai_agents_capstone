"""Unit tests for observability and tracer engine."""

import os
import pytest
from src.ai_agents_capstone.observability.tracer import Tracer
from src.ai_agents_capstone.models.trace import EventType


def test_tracer_lifecycle(tmp_path):
    tracer = Tracer(session_id="test_obs_sess", student_id="std_obs_01")
    tracer.record_tool_call(
        tool_name="analyze_readability",
        inputs={"text": "Hello world."},
        output={"fk_grade": 1.0},
        duration_ms=12.5,
        success=True,
    )
    tracer.record_agent_invocation(
        agent_name="IntakeAssessmentAgent",
        model_name="gemini-2.0-flash",
        duration_ms=250.0,
        prompt_tokens=100,
        completion_tokens=50,
    )
    tracer.record_state_transition("INIT", "DIAGNOSIS")
    trace = tracer.finish_session()

    assert trace.session_id == "test_obs_sess"
    assert trace.total_tool_calls == 1
    assert trace.total_tokens_consumed == 150
    assert len(trace.events) >= 3

    # Check export
    export_file = tmp_path / "test_trace.json"
    exported_path = tracer.export_trace(str(export_file))
    assert os.path.exists(exported_path)

    summary = tracer.get_summary_report()
    assert "OBSERVABILITY TRACE SUMMARY" in summary
    assert "IntakeAssessmentAgent" in summary
