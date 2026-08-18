# EduPathway AI — Implementation Roadmap

This roadmap breaks down the build of **EduPathway AI** into sequential, testable milestones designed to fulfill all 95 points of the capstone rubric.

---

## Phase 1: Core Schemas, Models & Configuration
- [ ] Define `config.py` with model selection (`gemini-2.0-flash`, `gemini-2.0-pro`, or overrides), API keys, and environment variables.
- [ ] Define Pydantic models in `src/ai_agents_capstone/models/`:
  - `profile.py`: `StudentProfile`, `IEPAccommodation`, `MasteryVector`, `CognitiveIndicator`.
  - `assessment.py`: `QuizSubmission`, `AssessmentReport`, `LearningGap`, `Misconception`.
  - `curriculum.py`: `LessonPlan`, `ScaffoldedSection`, `PracticeExercise`, `AccommodationApplication`.
  - `trace.py`: `TraceEvent`, `AgentTrace`, `ToolExecutionTrace`, `SessionTrace`.

## Phase 2: Custom Tools Registry (Rubric Pillar 1)
- [ ] `readability.py`: Implement Flesch-Kincaid grade level, Flesch reading ease, and Lexile score calculators with syllable counters.
- [ ] `standards.py`: Common Core & state educational standards knowledge base + search tool.
- [ ] `accommodations.py`: IEP accommodation compliance checker (validates that chunks, font/spacing guidelines, and visual cues exist in lessons).
- [ ] `assessment_tool.py`: Diagnostic generator tool with calibrated difficulty and scoring rubric.
- [ ] Comprehensive unit tests in `tests/test_tools.py`.

## Phase 3: Memory & Context Engine (Rubric Pillar 2)
- [ ] `session_memory.py`: Short-term rolling buffer with auto-summarization and token budget guards.
- [ ] `profile_store.py`: Long-term persistent store for student profiles, mastery vectors, and session histories (supports local JSON/SQLite with Firestore interface readiness).
- [ ] Unit tests in `tests/test_memory.py`.

## Phase 4: Specialized Agents & Prompts (Rubric Pillar 3)
- [ ] `base.py`: Base agent class handling SDK calls (`google-genai`), system instructions, structured output parsing, and error fallback.
- [ ] `intake_agent.py`: Evaluates diagnostic quizzes, identifies misconception categories, and calculates reading level mismatches.
- [ ] `curriculum_agent.py`: Synthesizes IEP-adapted lesson plans and scaffolded practice problem sets using standards lookup.
- [ ] `tutor_agent.py`: Interactive Socratic tutor with 3-tier hinting system, pedagogical guardrails, and positive reinforcement.
- [ ] Unit tests in `tests/test_agents.py`.

## Phase 5: Multi-Agent Orchestration & HITL Governance (Rubric Pillar 3)
- [ ] `hitl.py`: Policy engine detecting triggers for educator approval (e.g., accommodation alterations, grade band adjustments).
- [ ] `supervisor.py`: State-machine orchestrator coordinating end-to-end flow:
  `Diagnostic -> Curriculum Plan -> HITL Check -> Socratic Tutoring Session -> Profile Update`.
- [ ] Unit tests in `tests/test_orchestration.py`.

## Phase 6: Observability & Telemetry (Rubric Pillar 4)
- [ ] `tracer.py`: Structured event logging, latency measurement, token usage tracking, and trace export to `traces/`.
- [ ] Real-time session analytics summary generator.
- [ ] Unit tests in `tests/test_observability.py`.

## Phase 7: Rich User Interface & Demo Scenarios
- [ ] `ui/cli.py`: Interactive CLI with Rich formatting, colored dialogue boxes, student vs. educator mode, and live trace display.
- [ ] Sample datasets in `data/sample_students.json` (e.g., Grade 5 student with Dyslexia/ADHD accommodations struggling with Fraction addition).
- [ ] `main.py` integration wiring CLI, Orchestrator, and Memory.

## Phase 8: Infrastructure, CI/CD & Automated Evals (Rubric Pillar 5)
- [ ] GitHub Actions CI workflow in `.github/workflows/ci.yml` (Linting with `ruff`, Type checking, `pytest`, and Eval checks).
- [ ] `evals/run_evals.py`: Automated benchmark evaluation testing agent outputs against golden rubrics.
- [ ] `Dockerfile` and `docker-compose.yml` for reproducible packaging.
- [ ] Updated `README.md` with architecture diagrams, video script outline, and quickstart commands.
