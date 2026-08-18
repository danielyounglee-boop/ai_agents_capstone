"""Unit tests for supervisor orchestration and HITL policy engine."""

import pytest
from src.ai_agents_capstone.orchestration.supervisor import EduPathwaySupervisor
from src.ai_agents_capstone.orchestration.hitl import HITLPolicyEngine
from src.ai_agents_capstone.models.assessment import QuizSubmission, QuestionResponse, AssessmentReport
from src.ai_agents_capstone.models.curriculum import LessonPlan, StandardAlignment
from src.ai_agents_capstone.models.profile import StudentProfile


def test_hitl_cognitive_overload_trigger():
    report = AssessmentReport(
        student_id="s1",
        assessment_id="a1",
        subject="Math",
        topic="fractions",
        overall_accuracy_percentage=10.0,
        assessed_reading_level=4.0,
        cognitive_load_estimate=0.92,
        recommended_next_step="Pause",
        raw_diagnostic_summary="Overloaded",
    )
    profile = StudentProfile(student_id="s1", name="Sam", grade_level=5, reading_grade_level=4.0)

    proposal = HITLPolicyEngine.evaluate_assessment_policy(report, profile)
    assert proposal is not None
    assert "cognitive load" in proposal.trigger_reason.lower()


def test_hitl_grade_band_discrepancy_trigger():
    lesson = LessonPlan(
        lesson_id="l1",
        student_id="s1",
        title="Advanced Calculus",
        subject="Math",
        target_skill="Calculus",
        target_reading_level=5.0,
        aligned_standards=[
            StandardAlignment(code="MATH.HS", description="High School Standard", grade_level=11, subject="Math")
        ],
        educator_notes="",
    )
    profile = StudentProfile(student_id="s1", name="Sam", grade_level=5, reading_grade_level=4.0)

    proposal = HITLPolicyEngine.evaluate_curriculum_policy(lesson, profile)
    assert proposal is not None
    assert "differing by 2+ grade bands" in proposal.trigger_reason


def test_supervisor_end_to_end_flow():
    supervisor = EduPathwaySupervisor()
    submission = QuizSubmission(
        student_id="leo_m",
        quiz_id="quiz_test",
        subject="Mathematics",
        topic="fractions_addition_unlike_denominators",
        grade_target=5,
        responses=[
            QuestionResponse(
                question_id="q1",
                question_text="What is 1/2 + 1/4?",
                target_concept="finding common denominators",
                student_answer="2/6",
                correct_answer="3/4",
            )
        ],
    )
    result = supervisor.run_full_diagnostic_and_curriculum_flow(submission)
    assert result["session_id"] is not None
    assert result["assessment_report"] is not None
    assert result["lesson_plan"] is not None
    assert "trace_summary" in result
