"""Integration tests for the ADK agent application."""

import pytest
from app.agent import root_agent, app


def test_root_agent_structure():
    """Verify ADK root agent configuration and sub-agent hierarchy."""
    assert root_agent.name == "edupathway_supervisor"
    assert len(root_agent.sub_agents) == 3
    subagent_names = [sa.name for sa in root_agent.sub_agents]
    assert "intake_assessment_agent" in subagent_names
    assert "curriculum_synthesizer_agent" in subagent_names
    assert "socratic_tutor_agent" in subagent_names


def test_app_initialization():
    """Verify ADK App wrapper."""
    assert app.name == "app"
    assert app.root_agent is not None
    assert app.root_agent.name == "edupathway_supervisor"
