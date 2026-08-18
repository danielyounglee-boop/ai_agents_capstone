"""Unit tests for tool registry with guided error recovery validation."""

import pytest
from src.ai_agents_capstone.tools.readability import analyze_readability, count_syllables
from src.ai_agents_capstone.tools.standards import lookup_educational_standards
from src.ai_agents_capstone.tools.accommodations import validate_iep_accommodations
from src.ai_agents_capstone.tools.assessment_tool import generate_diagnostic_quiz
from src.ai_agents_capstone.tools.exporter import export_lesson_plan


def test_count_syllables():
    assert count_syllables("fraction") == 2
    assert count_syllables("denominator") >= 4
    assert count_syllables("math") == 1


def test_analyze_readability():
    text = "The dog ran up the hill. It was a sunny day."
    res = analyze_readability(text)
    assert res["status"] == "success"
    assert res["word_count"] > 0
    assert res["sentence_count"] == 2
    assert res["flesch_kincaid_grade_level"] <= 4.0
    assert "estimated_lexile" in res


def test_analyze_readability_guided_error():
    """Verify guided error recovery when empty/invalid text is provided."""
    res = analyze_readability("")
    assert res["status"] == "error_guided_recovery"
    assert "guided_recovery" in res
    assert "error_code" in res


def test_lookup_educational_standards():
    standards = lookup_educational_standards(grade_level=5, topic="fractions")
    assert len(standards) >= 1
    assert standards[0]["code"] == "CCSS.MATH.CONTENT.5.NF.A.1"
    assert "denominator" in standards[0]["description"].lower()


def test_lookup_educational_standards_guided_error():
    """Verify guided error recovery when invalid grade or query is provided."""
    res = lookup_educational_standards(grade_level=99)
    assert len(res) == 1
    assert res[0]["status"] == "error_guided_recovery"
    assert "guided_recovery" in res[0]


def test_validate_iep_accommodations_compliant():
    lesson = "Step 1: Look at the visual fraction bar diagram. Step 2: Notice how it looks like a space rocket fuel tank."
    accommodations = ["visual_scaffolding", "chunked_instructions", "high_interest_analogy"]
    res = validate_iep_accommodations(lesson, accommodations)
    assert res["is_compliant"] is True
    assert res["compliance_score"] == 100.0


def test_validate_iep_accommodations_missing_guided_remediation():
    lesson = "Just calculate the answer directly without any steps."
    accommodations = ["visual_scaffolding", "chunked_instructions"]
    res = validate_iep_accommodations(lesson, accommodations)
    assert res["is_compliant"] is False
    assert len(res["missing_accommodations"]) > 0
    assert "guided_recovery" in res
    assert len(res["recommendations"]) > 0


def test_generate_diagnostic_quiz():
    quiz = generate_diagnostic_quiz(topic="fractions", grade_level=5, num_questions=2)
    assert quiz["status"] == "success"
    assert len(quiz["questions"]) == 2
    assert quiz["grade_level"] == 5


def test_export_lesson_plan_guided_error():
    """Verify exporter returns guided recovery on empty data."""
    res = export_lesson_plan({})
    assert res["status"] == "error_guided_recovery"
    assert "guided_recovery" in res
