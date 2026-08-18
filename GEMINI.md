# Coding Agent Guide for EduPathway AI

## Project Overview
EduPathway AI is an autonomous multi-agent educational copilot and interactive student tutor built with Google Agent Development Kit (ADK) 2.0.

## Project Structure
- `app/agent.py`: ADK root agent (`edupathway_supervisor`) and sub-agents (`intake_assessment_agent`, `curriculum_synthesizer_agent`, `socratic_tutor_agent`).
- `src/ai_agents_capstone/`: Core business logic, custom tool registry, persistent memory, supervisor, and tracer.
- `tests/eval/`: ADK automated evaluation datasets and LLM-as-a-judge scoring configs.
- `tests/unit/`: Unit tests for tools, memory, agents, and observability.
- `tests/integration/`: Integration tests verifying multi-agent workflow.

## Development Commands
| Command | Purpose |
|---|---|
| `agents-cli playground` | Start the local agent playground |
| `uv run pytest tests/` | Run unit and integration test suite |
| `agents-cli eval generate` | Run agent inference over eval cases |
| `agents-cli eval grade` | Grade generated traces |
| `agents-cli deploy --dry-run` | Check Agent Runtime deployment readiness |
