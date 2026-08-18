"""Interactive Socratic Tutor Agent with pedagogical guardrails."""

import json
from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel, Field

from .base import BaseAgent
from ..models.curriculum import PracticeExercise, LessonPlan
from ..models.profile import StudentProfile
from ..memory.session_memory import SessionMemory
from ..observability.tracer import Tracer


class TutorTurnResponse(BaseModel):
    """Structured response from the Socratic Tutor."""

    response_text: str = Field(description="The conversational text shown to the student.")
    hint_tier_used: Optional[int] = Field(default=None, description="1, 2, or 3 if a hint was provided")
    is_answer_correct: Optional[bool] = None
    frustration_detected: bool = False
    suggest_break: bool = False
    mastery_demonstrated: bool = False


class SocraticTutorAgent(BaseAgent):
    """Agent that conducts real-time Socratic tutoring with pedagogical guardrails."""

    def __init__(self, model_name: Optional[str] = None):
        system_prompt = (
            "You are the EduPathway Socratic Tutor. You guide students through learning and practice "
            "exercises with pedagogical excellence.\n"
            "STRICT PEDAGOGICAL GUARDRAILS:\n"
            "1. NEVER give the direct final answer away, even if the student begs or guesses wildly.\n"
            "2. Use guided Socratic questions to prompt the student to think.\n"
            "3. Progress through 3 hint tiers: Tier 1 (conceptual question) -> Tier 2 (strategy clue) -> Tier 3 (worked sub-step).\n"
            "4. Maintain a warm, encouraging, positive growth-mindset tone.\n"
            "5. If high frustration is detected, offer reassurance or a short sensory break."
        )
        super().__init__(
            name="SocraticTutorAgent",
            system_prompt=system_prompt,
            model_name=model_name,
        )

    def interact(
        self,
        student_message: str,
        current_exercise: PracticeExercise,
        profile: StudentProfile,
        memory: SessionMemory,
        attempt_count: int = 1,
        tracer: Optional[Tracer] = None,
    ) -> TutorTurnResponse:
        """Process student input and generate a pedagogical Socratic tutoring response."""
        # 1. Add student message to memory
        memory.add_message(role="user", content=student_message)

        # 2. Build tutoring context
        history = memory.get_formatted_history()
        prompt = (
            f"Student: {profile.name} (Grade {profile.grade_level}, Reading Level {profile.reading_grade_level})\n"
            f"Accommodations/Learning style: {profile.primary_disability_or_focus or 'Visual Learner'}\n"
            f"Current Practice Problem: {current_exercise.prompt}\n"
            f"Correct Solution Key: {current_exercise.solution_key}\n"
            f"Scaffolding Hints Available:\n"
            f" - Tier 1: {current_exercise.hint_tier_1_concept}\n"
            f" - Tier 2: {current_exercise.hint_tier_2_strategy}\n"
            f" - Tier 3: {current_exercise.hint_tier_3_substep}\n"
            f"Current Attempt Count on this problem: {attempt_count}\n"
            f"Student's latest message: \"{student_message}\"\n\n"
            f"Provide a Socratic response following all pedagogical guardrails."
        )

        response_text = self.call_gemini(prompt=prompt, schema=TutorTurnResponse, tracer=tracer)

        try:
            data = json.loads(response_text)
            tutor_resp = TutorTurnResponse.model_validate(data)
        except Exception:
            tutor_resp = self._fallback_tutor(student_message, current_exercise, attempt_count)

        # 3. Add tutor response to memory
        memory.add_message(role="assistant", content=tutor_resp.response_text)

        return tutor_resp

    def _generate_simulated_fallback(self, prompt: str, schema: Optional[Type[BaseModel]]) -> str:
        """Deterministic simulation for offline/test environments."""
        # Extract student message line from prompt
        msg_line = ""
        for line in prompt.split("\n"):
            if "Student's latest message:" in line:
                msg_line = line.lower()
                break

        if "3/4" in msg_line or "3/6" in msg_line or "5/6" in msg_line or "7/10" in msg_line:
            mock_tutor = {
                "response_text": "🌟 Fantastic job! You found the common denominator and solved the problem accurately! What was your thought process?",
                "hint_tier_used": None,
                "is_answer_correct": True,
                "frustration_detected": False,
                "suggest_break": False,
                "mastery_demonstrated": True,
            }
        else:
            mock_tutor = {
                "response_text": "I hear you, and we will take it one step at a time! Before adding the pieces together, how can we make sure both fractions have the exact same bottom number (denominator)?",
                "hint_tier_used": 1,
                "is_answer_correct": False,
                "frustration_detected": False,
                "suggest_break": False,
                "mastery_demonstrated": False,
            }
        return json.dumps(mock_tutor)

    def _fallback_tutor(
        self,
        student_msg: str,
        exercise: PracticeExercise,
        attempt: int,
    ) -> TutorTurnResponse:
        """Rule-based fallback for Socratic responses."""
        ans = exercise.solution_key.lower().strip()
        cleaned_msg = student_msg.lower().strip()

        if ans in cleaned_msg or (ans.split()[0] in cleaned_msg if ans else False):
            return TutorTurnResponse(
                response_text=f"🎉 Outstanding work! That is correct ({exercise.solution_key})! You mastered this concept.",
                hint_tier_used=None,
                is_answer_correct=True,
                mastery_demonstrated=True,
            )

        if attempt == 1:
            return TutorTurnResponse(
                response_text=f"Great effort! Let's think about this: {exercise.hint_tier_1_concept}",
                hint_tier_used=1,
                is_answer_correct=False,
            )
        elif attempt == 2:
            return TutorTurnResponse(
                response_text=f"You're making progress! Here is a strategy hint: {exercise.hint_tier_2_strategy}",
                hint_tier_used=2,
                is_answer_correct=False,
            )
        else:
            return TutorTurnResponse(
                response_text=f"Let's work through the first part together: {exercise.hint_tier_3_substep} What do you get next?",
                hint_tier_used=3,
                is_answer_correct=False,
            )
