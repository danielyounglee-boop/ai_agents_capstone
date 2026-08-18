# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from src.ai_agents_capstone.tools.readability import analyze_readability
from src.ai_agents_capstone.tools.standards import lookup_educational_standards
from src.ai_agents_capstone.tools.accommodations import validate_iep_accommodations
from src.ai_agents_capstone.tools.assessment_tool import generate_diagnostic_quiz
from src.ai_agents_capstone.tools.exporter import export_lesson_plan

MODEL_FAST = os.getenv("MODEL_FAST", "gemini-3.6-flash")
MODEL_REASONING = os.getenv("MODEL_REASONING", "gemini-3.6-pro")

# 1. Intake & Diagnostic Assessment Sub-Agent
intake_subagent = Agent(
    name="intake_assessment_agent",
    model=Gemini(
        model=MODEL_FAST,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Evaluates student diagnostic quiz submissions, detects arithmetic slips vs. conceptual gaps, and measures reading level barriers.",
    instruction=(
        "You are the Intake & Assessment Specialist for EduPathway AI. Analyze baseline quiz submissions "
        "and calculate readability of prompts using the analyze_readability tool. Identify specific foundational "
        "skill gaps and cognitive fatigue indicators."
    ),
    tools=[analyze_readability, generate_diagnostic_quiz],
)

# 2. Curriculum Synthesizer Sub-Agent
curriculum_subagent = Agent(
    name="curriculum_synthesizer_agent",
    model=Gemini(
        model=MODEL_REASONING,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Synthesizes standards-aligned, scaffolded lesson plans tailored to student IEP accommodations.",
    instruction=(
        "You are the Curriculum Synthesizer for EduPathway AI. Ingest diagnostic gap reports and student IEP profiles. "
        "Lookup educational standards using lookup_educational_standards, embed explicit accommodations (visual fraction bars, "
        "chunking, high-interest analogies), validate accommodations using validate_iep_accommodations, and export lesson plans using export_lesson_plan."
    ),
    tools=[lookup_educational_standards, validate_iep_accommodations, export_lesson_plan],
)

# 3. Interactive Socratic Tutor Sub-Agent
socratic_tutor_subagent = Agent(
    name="socratic_tutor_agent",
    model=Gemini(
        model=MODEL_FAST,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Interactive conversational tutor with strict pedagogical guardrails (never gives away answers; uses 3-tier guided hints).",
    instruction=(
        "You are the Socratic Tutor for EduPathway AI. Guide students through practice exercises with encouragement.\n"
        "STRICT PEDAGOGICAL GUARDRAILS:\n"
        "1. NEVER reveal the direct final answer, even if requested.\n"
        "2. Provide 3-tier adaptive hints: Tier 1 (concept question) -> Tier 2 (strategy clue) -> Tier 3 (worked sub-step).\n"
        "3. Keep language accessible to the student's reading grade level."
    ),
    tools=[],
)

# Root Orchestrator Agent for EduPathway AI
root_agent = Agent(
    name="edupathway_supervisor",
    model=Gemini(
        model=MODEL_FAST,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="EduPathway AI Root Orchestrator for adaptive special education learning, IEP tailoring, and Socratic tutoring.",
    instruction=(
        "You are the EduPathway AI Supervisor. You coordinate the specialized multi-agent workflow:\n"
        "1. Delegate diagnostic evaluation to intake_assessment_agent.\n"
        "2. Delegate personalized lesson plan generation to curriculum_synthesizer_agent.\n"
        "3. Delegate real-time student practice and tutoring to socratic_tutor_agent.\n"
        "4. Enforce Human-in-the-Loop (HITL) policies whenever grade bands or IEP accommodations are modified."
    ),
    tools=[
        analyze_readability,
        lookup_educational_standards,
        validate_iep_accommodations,
        generate_diagnostic_quiz,
        export_lesson_plan,
    ],
    sub_agents=[
        intake_subagent,
        curriculum_subagent,
        socratic_tutor_subagent,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
