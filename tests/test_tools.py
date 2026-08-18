"""Unit tests for tool registry."""

import pytest
from src.ai_agents_capstone.tools.readability import analyze_readability, count_syllables
from src.ai_agents_capstone.tools.standards import lookup_educational_standards
from src.ai_agents_capstone.tools.accommodations import validate_iep_accommodations
from src.ai_agents_capstone.tools.assessment_tool import generate_diagnostic_quiz


def test_count_syllables():
    assert count_syllables("fraction") == 2
    assert count_syllables("denominator") >= 4
    assert count_syllables("math") == 1


def test_analyze_readability():
    text = "The dog ran up the hill. It was a sunny day."
    res = analyze_readability(text)
    assert res["word_count"] > 0
    assert res["sentence_count"] == 2
    assert res["flesch_kincaid_grade_level"] <= 4.0
    assert "Lexile" in res or "estimated_lexile" in res


def test_lookup_educational_standards():
    standards = lookup_educational_standards(grade_level=5, topic="fractions")
    assert len(standards) >= 1
    assert standards[0]["code"] == "CCSS.MATH.CONTENT.5.NF.A.1"
    assert "denominator" in standards[0]["description"].lower()


def test_validate_iep_accommodations_compliant():
    lesson = "Step 1: Look at the visual fraction bar diagram. Step 2: Notice how it looks like a space rocket fuel tank."
    accommodations = ["visual_scaffolding", "chunked_instructions", "high_interest_analogy"]
    res = validate_iep_accommodations(lesson, accommodations)
    assert res["is_compliant"] is True
    assert res["compliance_score"] == 100.0


def test_validate_iep_accommodations_missing():
    lesson = "Just calculate the answer directly without any steps."
    accommodations = ["visual_scaffolding", "chunked_instructions"]
    res = validate_iep_accommodations(lesson, accommodations)
    assert res["is_compliant"] is False
    assert len(res["missing_accommodations"]) > 0


def test_generate_diagnostic_quiz():
    quiz = generate_diagnostic_quiz(topic="fractions", grade_level=5, num_questions=2)
    assert len(quiz["questions"]) == 2
    assert quiz["grade_level"] == 5
