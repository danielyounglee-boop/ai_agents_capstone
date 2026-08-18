"""Unit tests for specialized agents."""

import pytest
from src.ai_agents_capstone.agents.intake_agent import IntakeAssessmentAgent
from src.ai_agents_capstone.agents.curriculum_agent import CurriculumSynthesizerAgent
from src.ai_agents_capstone.agents.tutor_agent import SocraticTutorAgent
from src.ai_agents_capstone.models.assessment import QuizSubmission, QuestionResponse
from src.ai_agents_capstone.models.curriculum import PracticeExercise
from src.ai_agents_capstone.models.profile import StudentProfile
from src.ai_agents_capstone.memory.session_memory import SessionMemory


def test_intake_assessment_agent():
    agent = IntakeAssessmentAgent()
    submission = QuizSubmission(
        student_id="leo_m",
        quiz_id="quiz_01",
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
    report = agent.evaluate_quiz(submission)
    assert report.student_id == "leo_m"
    assert report.assessed_reading_level > 0
    assert len(report.learning_gaps) >= 1


def test_curriculum_synthesizer_agent():
    agent = CurriculumSynthesizerAgent()
    agent_intake = IntakeAssessmentAgent()
    submission = QuizSubmission(
        student_id="leo_m",
        quiz_id="quiz_01",
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
    report = agent_intake.evaluate_quiz(submission)
    profile = StudentProfile(
        student_id="leo_m",
        name="Leo",
        grade_level=5,
        reading_grade_level=3.6,
        interests=["Space"],
    )
    lesson = agent.synthesize_lesson(report, profile)
    assert lesson.student_id == "leo_m"
    assert len(lesson.sections) >= 1
    assert len(lesson.practice_exercises) >= 1


def test_socratic_tutor_guardrails():
    tutor = SocraticTutorAgent()
    memory = SessionMemory(session_id="test_tutor")
    exercise = PracticeExercise(
        exercise_id="ex_01",
        prompt="What is 1/2 + 1/4?",
        difficulty_level="scaffolded",
        hint_tier_1_concept="Think about equivalent fourths for 1/2.",
        hint_tier_2_strategy="Convert 1/2 to 2/4.",
        hint_tier_3_substep="2/4 + 1/4 = ?",
        solution_key="3/4",
    )
    profile = StudentProfile(student_id="leo_m", name="Leo", grade_level=5, reading_grade_level=3.6)

    # Attempt 1: Begging for answer
    resp1 = tutor.interact("I don't know, just tell me the answer!", exercise, profile, memory, attempt_count=1)
    assert "3/4" not in resp1.response_text
    assert resp1.hint_tier_used == 1

    # Attempt 2: Correct answer
    resp2 = tutor.interact("Is it 3/4?", exercise, profile, memory, attempt_count=2)
    assert resp2.is_answer_correct is True or resp2.mastery_demonstrated is True
