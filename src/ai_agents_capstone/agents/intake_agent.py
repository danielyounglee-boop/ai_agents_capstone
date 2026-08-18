"""Intake & Diagnostic Assessment Agent."""

import json
from typing import Optional, Type
from pydantic import BaseModel

from .base import BaseAgent
from ..models.assessment import QuizSubmission, AssessmentReport, LearningGap, Misconception
from ..models.profile import StudentProfile
from ..tools.readability import analyze_readability
from ..observability.tracer import Tracer


class IntakeAssessmentAgent(BaseAgent):
    """Agent that analyzes baseline quizzes, identifies misconceptions, and estimates reading levels."""

    def __init__(self, model_name: Optional[str] = None):
        system_prompt = (
            "You are the EduPathway Intake & Assessment Specialist. Your goal is to evaluate student "
            "diagnostic assessments, identify foundational learning gaps vs. arithmetic slips, determine "
            "if text readability posed an obstacle, and output a structured AssessmentReport."
        )
        super().__init__(
            name="IntakeAssessmentAgent",
            system_prompt=system_prompt,
            model_name=model_name,
            tools=[analyze_readability],
        )

    def evaluate_quiz(
        self,
        submission: QuizSubmission,
        profile: Optional[StudentProfile] = None,
        tracer: Optional[Tracer] = None,
    ) -> AssessmentReport:
        """Analyze a quiz submission and produce a structured diagnostic AssessmentReport."""
        # 1. Use Readability tool to measure prompt difficulty
        all_prompt_text = " ".join([r.question_text for r in submission.responses])
        readability = self.execute_tool("analyze_readability", {"text": all_prompt_text}, tracer=tracer)
        assessed_reading_level = readability["flesch_kincaid_grade_level"]

        # 2. Build prompt for Gemini
        prompt = (
            f"Analyze the following student quiz submission:\n"
            f"Student ID: {submission.student_id}\n"
            f"Subject: {submission.subject}\n"
            f"Topic: {submission.topic}\n"
            f"Target Grade: {submission.grade_target}\n"
            f"Reading Level of Prompts: {assessed_reading_level} (FK Grade)\n\n"
            f"Responses:\n"
        )
        for r in submission.responses:
            prompt += f"- Question: {r.question_text} | Student Answer: {r.student_answer} | Correct: {r.correct_answer}\n"

        prompt += "\nProduce a comprehensive diagnostic report identifying learning gaps and conceptual misconceptions."

        # 3. Call LLM
        response_text = self.call_gemini(prompt=prompt, schema=AssessmentReport, tracer=tracer)

        try:
            data = json.loads(response_text)
            data["student_id"] = submission.student_id
            report = AssessmentReport.model_validate(data)
        except Exception:
            report = self._fallback_report(submission, assessed_reading_level)

        report.student_id = submission.student_id

        return report

    def _generate_simulated_fallback(self, prompt: str, schema: Optional[Type[BaseModel]]) -> str:
        """Deterministic simulation for offline/test environments."""
        mock_report = {
            "student_id": "std_sample_01",
            "assessment_id": "rep_diag_frac_01",
            "subject": "Mathematics",
            "topic": "fractions_addition_unlike_denominators",
            "overall_accuracy_percentage": 33.3,
            "assessed_reading_level": 3.8,
            "learning_gaps": [
                {
                    "skill_id": "least_common_multiple",
                    "skill_name": "Finding Least Common Denominators",
                    "severity": "high",
                    "evidence": "Student added denominators across (e.g. 1/2 + 1/4 = 2/6).",
                    "recommended_prerequisite": "CCSS.MATH.CONTENT.4.NF.A.1 (Equivalent Fractions)",
                }
            ],
            "misconceptions": [
                {
                    "concept": "Fraction Addition",
                    "misconception_type": "add_denominators_directly",
                    "description": "Treats numerator and denominator as separate whole numbers without finding a common denominator unit.",
                    "correction_strategy": "Use visual fraction bars and high-interest pizza/space partitioning analogies.",
                }
            ],
            "cognitive_load_estimate": 0.75,
            "recommended_next_step": "Synthesize a 3-part scaffolded lesson on finding common denominators with visual fraction models.",
            "raw_diagnostic_summary": "Student struggles with unlike denominator addition due to missing equivalent fractions intuition.",
            "evaluated_at": "2026-08-18T00:00:00Z",
        }
        return json.dumps(mock_report)

    def _fallback_report(self, submission: QuizSubmission, reading_level: float) -> AssessmentReport:
        """Construct fallback AssessmentReport from submission data."""
        correct_count = sum(1 for r in submission.responses if r.student_answer.strip() == r.correct_answer.strip())
        total = max(1, len(submission.responses))
        accuracy = round((correct_count / total) * 100.0, 1)

        return AssessmentReport(
            student_id=submission.student_id,
            assessment_id=f"rep_{submission.quiz_id}",
            subject=submission.subject,
            topic=submission.topic,
            overall_accuracy_percentage=accuracy,
            assessed_reading_level=reading_level,
            learning_gaps=[
                LearningGap(
                    skill_id=f"gap_{submission.topic}",
                    skill_name=f"Mastery of {submission.topic}",
                    severity="high" if accuracy < 50 else "medium",
                    evidence=f"Scored {accuracy}% on baseline diagnostic.",
                    recommended_prerequisite="Foundational fraction scaling & equivalence",
                )
            ],
            misconceptions=[
                Misconception(
                    concept=submission.topic,
                    misconception_type="procedural_arithmetic_error",
                    description="Identified difficulty with procedural step execution under unlike units.",
                    correction_strategy="Visual scaffolding and step-by-step chunked guidance.",
                )
            ],
            cognitive_load_estimate=0.7 if accuracy < 50 else 0.4,
            recommended_next_step="Synthesize tailored lesson plan with concrete visual scaffolding.",
            raw_diagnostic_summary=f"Diagnostic completed: {correct_count}/{total} correct answers.",
        )
