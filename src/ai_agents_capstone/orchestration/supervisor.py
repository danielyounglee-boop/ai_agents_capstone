"""EduPathway Multi-Agent Supervisor and State Machine Orchestrator."""

import os
import uuid
from typing import Optional, Dict, Any, List

from ..models.assessment import QuizSubmission, AssessmentReport
from ..models.curriculum import LessonPlan, PracticeExercise
from ..models.profile import StudentProfile
from ..models.trace import SessionTrace
from ..agents.intake_agent import IntakeAssessmentAgent
from ..agents.curriculum_agent import CurriculumSynthesizerAgent
from ..agents.tutor_agent import SocraticTutorAgent, TutorTurnResponse
from ..memory.session_memory import SessionMemory
from ..memory.profile_store import StudentProfileStore
from ..observability.tracer import Tracer
from ..tools.exporter import export_lesson_plan
from .hitl import HITLPolicyEngine, EducatorProposal, HITLDecision


class EduPathwaySupervisor:
    """Central orchestrator driving multi-agent coordination, HITL gates, and memory updates."""

    def __init__(
        self,
        profile_store: Optional[StudentProfileStore] = None,
        intake_agent: Optional[IntakeAssessmentAgent] = None,
        curriculum_agent: Optional[CurriculumSynthesizerAgent] = None,
        tutor_agent: Optional[SocraticTutorAgent] = None,
    ):
        self.profile_store = profile_store or StudentProfileStore()
        self.intake_agent = intake_agent or IntakeAssessmentAgent()
        self.curriculum_agent = curriculum_agent or CurriculumSynthesizerAgent()
        self.tutor_agent = tutor_agent or SocraticTutorAgent()
        self.hitl_engine = HITLPolicyEngine()

    def run_full_diagnostic_and_curriculum_flow(
        self,
        submission: QuizSubmission,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute the end-to-end multi-agent pipeline from Diagnostic to Lesson Plan Synthesis."""
        sess_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"
        tracer = Tracer(session_id=sess_id, student_id=submission.student_id)
        tracer.record_state_transition("INIT", "DIAGNOSTIC_ASSESSMENT")

        # 1. Load or initialize profile
        profile = self.profile_store.get_profile(submission.student_id)
        if not profile:
            profile = StudentProfile(
                student_id=submission.student_id,
                name=f"Student {submission.student_id}",
                grade_level=submission.grade_target,
                reading_grade_level=float(submission.grade_target),
                interests=["Space Exploration", "Robotics", "Dinosaurs"],
            )
            self.profile_store.save_profile(profile)

        # 2. Intake & Assessment Agent
        tracer.emit_event(tracer.session_trace.events[0].event_type.AGENT_START, {"agent": "IntakeAssessmentAgent"})
        report: AssessmentReport = self.intake_agent.evaluate_quiz(submission, profile, tracer=tracer)

        # 3. Check Assessment HITL Policy
        hitl_assessment = self.hitl_engine.evaluate_assessment_policy(report, profile)
        if hitl_assessment:
            tracer.record_hitl(
                triggered=True,
                reason=hitl_assessment.trigger_reason,
                decision=hitl_assessment.decision.value,
                notes=hitl_assessment.proposed_change,
            )

        # 4. Curriculum Synthesizer Agent
        tracer.record_state_transition("DIAGNOSTIC_ASSESSMENT", "CURRICULUM_SYNTHESIS")
        lesson: LessonPlan = self.curriculum_agent.synthesize_lesson(report, profile, tracer=tracer)

        # 5. Check Curriculum HITL Policy
        hitl_curriculum = self.hitl_engine.evaluate_curriculum_policy(lesson, profile)
        if hitl_curriculum:
            tracer.record_hitl(
                triggered=True,
                reason=hitl_curriculum.trigger_reason,
                decision=hitl_curriculum.decision.value,
                notes=hitl_curriculum.proposed_change,
            )
            lesson.requires_hitl_approval = True
            lesson.hitl_reason = hitl_curriculum.trigger_reason

        # 6. Export Lesson Plan Artifacts
        exported_path = export_lesson_plan(lesson.model_dump(), output_dir="data/lessons")

        # 7. Finalize trace
        tracer.record_state_transition("CURRICULUM_SYNTHESIS", "READY_FOR_TUTORING")
        trace_summary = tracer.finish_session()

        return {
            "session_id": sess_id,
            "student_profile": profile,
            "assessment_report": report,
            "lesson_plan": lesson,
            "exported_lesson_path": exported_path,
            "hitl_proposals": [p for p in [hitl_assessment, hitl_curriculum] if p is not None],
            "trace_summary": tracer.get_summary_report(),
            "trace_filepath": os.path.abspath(f"traces/trace_{sess_id}.json"),
        }

    def conduct_tutoring_turn(
        self,
        student_id: str,
        exercise: PracticeExercise,
        student_message: str,
        memory: SessionMemory,
        attempt_count: int = 1,
        tracer: Optional[Tracer] = None,
    ) -> TutorTurnResponse:
        """Run a single interactive Socratic tutoring turn."""
        profile = self.profile_store.get_profile(student_id)
        if not profile:
            raise ValueError(f"Student '{student_id}' not found.")

        response = self.tutor_agent.interact(
            student_message=student_message,
            current_exercise=exercise,
            profile=profile,
            memory=memory,
            attempt_count=attempt_count,
            tracer=tracer,
        )

        # If student demonstrated mastery, update mastery vector in long-term memory
        if response.mastery_demonstrated:
            topic_key = exercise.exercise_id
            self.profile_store.update_mastery(
                student_id=student_id,
                topic_id=topic_key,
                topic_name=exercise.prompt[:30],
                new_score=1.0,
            )

        return response
