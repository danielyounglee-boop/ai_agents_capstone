"""Student IEP Profile and Mastery models for EduPathway AI."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class IEPAccommodation(BaseModel):
    """Formal IEP accommodation specification."""

    category: str = Field(description="Category e.g. presentation, response, timing, setting")
    description: str = Field(description="Description of accommodation")
    guidelines: List[str] = Field(default_factory=list, description="Specific action items")


class MasteryVector(BaseModel):
    """Learning mastery vector across domain topics (score 0.0 to 1.0)."""

    topic_id: str
    topic_name: str
    mastery_score: float = Field(ge=0.0, le=1.0, description="0.0 = Novice, 1.0 = Mastered")
    attempts_count: int = 0
    last_evaluated: datetime = Field(default_factory=datetime.utcnow)


class CognitiveIndicator(BaseModel):
    """Cognitive fatigue and frustration trend indicators."""

    session_id: str
    frustration_level: float = Field(ge=0.0, le=1.0, description="0.0 = Calm/Engaged, 1.0 = Overwhelmed")
    attention_span_minutes: int = Field(default=20)
    preferred_modality: str = Field(default="visual", description="visual, auditory, hands-on, reading")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StudentProfile(BaseModel):
    """Comprehensive Student Profile for personalized learning and IEP compliance."""

    student_id: str
    name: str
    grade_level: int = Field(ge=1, le=12)
    reading_grade_level: float = Field(description="Assessed reading grade level e.g. 3.5")
    primary_disability_or_focus: Optional[str] = Field(
        default=None, description="e.g. Dyslexia, ADHD, Dyscalculia, ELL"
    )
    interests: List[str] = Field(default_factory=list, description="High-interest topics for analogies (e.g. dinosaurs, space)")
    accommodations: List[IEPAccommodation] = Field(default_factory=list)
    mastery_vectors: Dict[str, MasteryVector] = Field(default_factory=dict)
    cognitive_history: List[CognitiveIndicator] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
