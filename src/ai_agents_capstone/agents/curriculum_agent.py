"""Curriculum Synthesizer Agent for generating scaffolded, IEP-compliant lesson plans."""

import json
from typing import Optional, Type, List
from pydantic import BaseModel

from .base import BaseAgent
from ..models.assessment import AssessmentReport
from ..models.curriculum import LessonPlan, ScaffoldedSection, PracticeExercise, StandardAlignment
from ..models.profile import StudentProfile
from ..tools.standards import lookup_educational_standards
from ..tools.accommodations import validate_iep_accommodations
from ..observability.tracer import Tracer


class CurriculumSynthesizerAgent(BaseAgent):
    """Agent that creates personalized, scaffolded lesson plans and exercises adhering to IEP guidelines."""

    def __init__(self, model_name: Optional[str] = None):
        system_prompt = (
            "You are the EduPathway Curriculum Synthesizer. You create highly engaging, step-by-step, "
            "scaffolded lesson plans aligned with educational standards and strictly tailored to student "
            "IEP accommodations, reading level constraints, and personal high-interest analogies."
        )
        super().__init__(
            name="CurriculumSynthesizerAgent",
            system_prompt=system_prompt,
            model_name=model_name,
            tools=[lookup_educational_standards, validate_iep_accommodations],
        )

    def synthesize_lesson(
        self,
        report: AssessmentReport,
        profile: StudentProfile,
        tracer: Optional[Tracer] = None,
    ) -> LessonPlan:
        """Generate a personalized lesson plan for a student based on diagnostic gaps and IEP profile."""
        # 1. Lookup standards
        standards_raw = self.execute_tool(
            "lookup_educational_standards",
            {"grade_level": profile.grade_level, "subject": report.subject, "topic": report.topic},
            tracer=tracer,
        )
        aligned_standards = [
            StandardAlignment(
                code=s["code"],
                description=s["description"],
                grade_level=s["grade_level"],
                subject=s["subject"],
            )
            for s in standards_raw
        ]

        # 2. Extract accommodations
        accommodations_list = [f"{a.category}: {a.description}" for a in profile.accommodations]
        interests_str = ", ".join(profile.interests) if profile.interests else "space exploration, dinosaurs, robotics"

        # 3. Build synthesis prompt
        prompt = (
            f"Synthesize an adaptive, scaffolded lesson plan for student '{profile.name}' (Grade {profile.grade_level}).\n"
            f"Subject: {report.subject} | Target Topic: {report.topic}\n"
            f"Assessed Reading Level: Grade {profile.reading_grade_level}\n"
            f"Primary Focus / Accommodations: {profile.primary_disability_or_focus or 'General'}\n"
            f"Mandatory Accommodations: {accommodations_list}\n"
            f"High-Interest Themes for Analogies: {interests_str}\n"
            f"Diagnostic Gaps: {[g.skill_name for g in report.learning_gaps]}\n"
            f"Misconceptions to Address: {[m.description for m in report.misconceptions]}\n\n"
            f"Requirements:\n"
            f"1. Break the concept into chunked sub-steps (Step 1, Step 2, Step 3).\n"
            f"2. Integrate high-interest analogies based on student interests ({interests_str}).\n"
            f"3. Include visual descriptions or number-line models.\n"
            f"4. Provide 3 practice exercises with 3-tier Socratic hinting.\n"
        )

        response_text = self.call_gemini(prompt=prompt, schema=LessonPlan, tracer=tracer)

        try:
            data = json.loads(response_text)
            lesson = LessonPlan.model_validate(data)
        except Exception:
            lesson = self._fallback_lesson(report, profile, aligned_standards)

        # 4. Validate IEP accommodations using Tool
        full_lesson_text = (
            f"{lesson.title} "
            + " ".join([s.content for s in lesson.sections])
            + " ".join([p.prompt for p in lesson.practice_exercises])
        )
        validation_result = self.execute_tool(
            "validate_iep_accommodations",
            {"lesson_content": full_lesson_text, "required_accommodations": [a.category for a in profile.accommodations]},
            tracer=tracer,
        )

        if not validation_result["is_compliant"]:
            lesson.educator_notes += f" [Note: Accommodations check: {validation_result['compliance_score']}% compliant. Recommendations: {'; '.join(validation_result['recommendations'])}]"

        return lesson

    def _generate_simulated_fallback(self, prompt: str, schema: Optional[Type[BaseModel]]) -> str:
        """Deterministic simulation for offline/test environments."""
        mock_lesson = {
            "lesson_id": "les_frac_add_01",
            "student_id": "std_sample_01",
            "title": "Cosmic Fractions: Navigating Unlike Denominators with Space Stations",
            "subject": "Mathematics",
            "target_skill": "Adding fractions with unlike denominators using visual fraction bars",
            "aligned_standards": [
                {
                    "code": "CCSS.MATH.CONTENT.5.NF.A.1",
                    "description": "Add and subtract fractions with unlike denominators by finding common denominators.",
                    "grade_level": 5,
                    "subject": "Mathematics",
                }
            ],
            "target_reading_level": 3.8,
            "sections": [
                {
                    "section_id": "sec_01",
                    "title": "Step 1: The Space Docking Problem (Why Units Must Match)",
                    "content": "Imagine Rocket A carries 1/2 tank of fuel and Rocket B carries 1/4 tank. We cannot simply add the tank parts together directly because the containers are cut into different sized pieces! To combine them, we need both containers partitioned into the same size compartments (fourths).",
                    "analogy_or_theme": "Space station fuel docking",
                    "applied_accommodations": ["visual_scaffolding", "high_interest_analogy", "chunked_instructions"],
                    "check_for_understanding_question": "Why can't we add 1/2 and 1/4 by just adding 1+1 on top and 2+4 on bottom?",
                    "check_answer": "Because 1/2 and 1/4 represent different sized slices/pieces.",
                },
                {
                    "section_id": "sec_02",
                    "title": "Step 2: Scaling Fractions with Visual Fraction Bars",
                    "content": "Look at the visual fraction bar: 1/2 is the exact same length as 2/4. When we replace 1/2 with 2/4, our math problem becomes 2/4 + 1/4. Now that both parts have the common denominator 4, we simply add the numerators: 2 fourths + 1 fourth = 3 fourths (3/4).",
                    "analogy_or_theme": "Fraction length bars",
                    "applied_accommodations": ["visual_scaffolding", "chunked_instructions"],
                    "check_for_understanding_question": "What equivalent fraction with denominator 4 has the same value as 1/2?",
                    "check_answer": "2/4",
                },
            ],
            "practice_exercises": [
                {
                    "exercise_id": "prac_01",
                    "prompt": "Using a fraction bar model, find 1/3 + 1/6.",
                    "difficulty_level": "scaffolded",
                    "hint_tier_1_concept": "Can 1/3 be sliced into equal sixths?",
                    "hint_tier_2_strategy": "Multiply both numerator and denominator of 1/3 by 2 to find equivalent sixths.",
                    "hint_tier_3_substep": "1/3 = 2/6. Now compute 2/6 + 1/6.",
                    "solution_key": "3/6 (or 1/2 simplified)",
                    "visual_aid_description": "Fraction bar showing 1/3 divided into two 1/6 segments.",
                },
                {
                    "exercise_id": "prac_02",
                    "prompt": "Solve: 2/5 + 3/10",
                    "difficulty_level": "standard",
                    "hint_tier_1_concept": "What is the common denominator between 5 and 10?",
                    "hint_tier_2_strategy": "Convert 2/5 into tenths first.",
                    "hint_tier_3_substep": "2/5 * (2/2) = 4/10. Now add 4/10 + 3/10.",
                    "solution_key": "7/10",
                    "visual_aid_description": "Grid partitioned into 10 equal cells.",
                },
            ],
            "educator_notes": "Lesson plan integrates high-interest space theme, chunked steps, and visual representations for dyslexia/ADHD support.",
            "requires_hitl_approval": False,
            "hitl_reason": None,
            "created_at": "2026-08-18T00:00:00Z",
        }
        return json.dumps(mock_lesson)

    def _fallback_lesson(
        self,
        report: AssessmentReport,
        profile: StudentProfile,
        standards: List[StandardAlignment],
    ) -> LessonPlan:
        """Construct fallback LessonPlan."""
        interest = profile.interests[0] if profile.interests else "Space Explorer"
        return LessonPlan(
            lesson_id=f"les_{report.assessment_id}",
            student_id=profile.student_id,
            title=f"Adaptive Mastery: {report.topic.replace('_', ' ').title()}",
            subject=report.subject,
            target_skill=report.topic,
            aligned_standards=standards,
            target_reading_level=profile.reading_grade_level,
            sections=[
                ScaffoldedSection(
                    section_id="sec_01",
                    title="Step 1: Conceptual Foundation & Visual Model",
                    content=f"Let's explore {report.topic.replace('_', ' ')} using a {interest} analogy. Break the problem into equal parts using visual diagrams.",
                    analogy_or_theme=interest,
                    applied_accommodations=["chunked_instructions", "visual_scaffolding"],
                    check_for_understanding_question="What is the first step before combining unequal parts?",
                    check_answer="Make sure all pieces are equal units (common denominator).",
                )
            ],
            practice_exercises=[
                PracticeExercise(
                    exercise_id="prac_01",
                    prompt="What is 1/2 + 1/4?",
                    difficulty_level="scaffolded",
                    hint_tier_1_concept="Think about what 1/2 looks like when cut into fourths.",
                    hint_tier_2_strategy="Convert 1/2 into 2/4.",
                    hint_tier_3_substep="2/4 + 1/4 = ?",
                    solution_key="3/4",
                )
            ],
            educator_notes="Generated adaptive lesson scaffold with multi-tier hinting.",
        )
