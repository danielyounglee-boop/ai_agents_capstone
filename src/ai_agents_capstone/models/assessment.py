"""Diagnostic assessment and gap evaluation schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    """Student response to a single diagnostic question."""

    question_id: str
    question_text: str
    target_concept: str
    student_answer: str
    correct_answer: str
    is_correct: Optional[bool] = None
    student_work_steps: Optional[str] = None


class QuizSubmission(BaseModel):
    """Raw quiz submission from a student."""

    student_id: str
    quiz_id: str
    subject: str
    topic: str
    grade_target: int
    responses: List[QuestionResponse]
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class LearningGap(BaseModel):
    """Identified foundational skill gap."""

    skill_id: str
    skill_name: str
    severity: str = Field(description="low, medium, high, critical")
    evidence: str
    recommended_prerequisite: Optional[str] = None


class Misconception(BaseModel):
    """Specific conceptual error pattern."""

    concept: str
    misconception_type: str = Field(description="e.g. calculation_error, denominator_addition, sign_error")
    description: str
    correction_strategy: str


class AssessmentReport(BaseModel):
    """Standardized output from Intake & Assessment Agent."""

    student_id: str
    assessment_id: str
    subject: str
    topic: str
    overall_accuracy_percentage: float = Field(ge=0.0, le=100.0)
    assessed_reading_level: float
    learning_gaps: List[LearningGap] = Field(default_factory=list)
    misconceptions: List[Misconception] = Field(default_factory=list)
    cognitive_load_estimate: float = Field(ge=0.0, le=1.0, description="0.0 = effortless, 1.0 = cognitive overload")
    recommended_next_step: str
    raw_diagnostic_summary: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
