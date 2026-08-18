"""Human-in-the-Loop (HITL) Policy Engine and Proposal Generator."""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from ..models.profile import StudentProfile, IEPAccommodation
from ..models.curriculum import LessonPlan
from ..models.assessment import AssessmentReport


class HITLDecision(str, Enum):
    """Educator decision status."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class EducatorProposal(BaseModel):
    """Proposal requiring human educator review and approval before execution."""

    proposal_id: str
    student_id: str
    trigger_reason: str
    proposed_change: str
    risk_level: str = Field(description="low, medium, high")
    decision: HITLDecision = HITLDecision.PENDING
    educator_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class HITLPolicyEngine:
    """Evaluates multi-agent operations against safety and compliance policies."""

    @staticmethod
    def evaluate_assessment_policy(
        report: AssessmentReport,
        profile: StudentProfile,
    ) -> Optional[EducatorProposal]:
        """Check if diagnostic findings require educator intervention."""
        # Trigger 1: Extreme cognitive overload
        if report.cognitive_load_estimate >= 0.85:
            return EducatorProposal(
                proposal_id=f"hitl_cog_{report.assessment_id}",
                student_id=profile.student_id,
                trigger_reason="Severe cognitive load / frustration detected (score >= 0.85)",
                proposed_change="Pause session, insert a 5-minute sensory break, and reduce question difficulty by 1 grade level.",
                risk_level="medium",
            )

        # Trigger 2: Severe reading level mismatch
        if abs(report.assessed_reading_level - profile.reading_grade_level) > 2.0:
            return EducatorProposal(
                proposal_id=f"hitl_read_{report.assessment_id}",
                student_id=profile.student_id,
                trigger_reason=f"Significant reading level discrepancy: Material at Grade {report.assessed_reading_level} vs Student reading profile of Grade {profile.reading_grade_level}",
                proposed_change="Auto-reformat all lesson text and instructions down to Grade 3 readability.",
                risk_level="high",
            )

        return None

    @staticmethod
    def evaluate_curriculum_policy(
        lesson: LessonPlan,
        profile: StudentProfile,
    ) -> Optional[EducatorProposal]:
        """Check if synthesized curriculum plan modifies formal IEP parameters."""
        # Trigger: If lesson targets a grade level different from student profile
        for std in lesson.aligned_standards:
            if abs(std.grade_level - profile.grade_level) >= 2:
                return EducatorProposal(
                    proposal_id=f"hitl_grade_{lesson.lesson_id}",
                    student_id=profile.student_id,
                    trigger_reason=f"Curriculum standard '{std.code}' is set to Grade {std.grade_level}, differing by 2+ grade bands from student grade {profile.grade_level}.",
                    proposed_change="Require educator sign-off to teach off-grade-level standard under IEP pathway.",
                    risk_level="high",
                )

        return None
