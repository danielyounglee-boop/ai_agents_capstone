"""Curriculum, lesson plan, and accommodation schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class StandardAlignment(BaseModel):
    """Educational standard mapping."""

    code: str = Field(description="e.g. CCSS.MATH.CONTENT.5.NF.A.1")
    description: str
    grade_level: int
    subject: str


class PracticeExercise(BaseModel):
    """Calibrated practice question with multi-tier scaffolding hints."""

    exercise_id: str
    prompt: str
    difficulty_level: str = Field(description="scaffolded, standard, challenge")
    hint_tier_1_concept: str = Field(description="Gentle guiding question")
    hint_tier_2_strategy: str = Field(description="Process or decomposition clue")
    hint_tier_3_substep: str = Field(description="First step worked out")
    solution_key: str
    visual_aid_description: Optional[str] = None


class ScaffoldedSection(BaseModel):
    """Individual chunk or section of a personalized lesson."""

    section_id: str
    title: str
    content: str
    analogy_or_theme: Optional[str] = None
    applied_accommodations: List[str] = Field(default_factory=list)
    check_for_understanding_question: str
    check_answer: str


class LessonPlan(BaseModel):
    """Full personalized, IEP-compliant lesson plan synthesized for a student."""

    lesson_id: str
    student_id: str
    title: str
    subject: str
    target_skill: str
    aligned_standards: List[StandardAlignment] = Field(default_factory=list)
    target_reading_level: float
    sections: List[ScaffoldedSection] = Field(default_factory=list)
    practice_exercises: List[PracticeExercise] = Field(default_factory=list)
    educator_notes: str
    requires_hitl_approval: bool = False
    hitl_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
