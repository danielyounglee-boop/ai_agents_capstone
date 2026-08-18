"""Diagnostic quiz generator tool for baseline student assessment with guided error recovery."""

from typing import Dict, Any, List


DIAGNOSTIC_BANK: Dict[str, List[Dict[str, Any]]] = {
    "fractions_addition_unlike_denominators": [
        {
            "question_id": "diag_frac_01",
            "question_text": "What is 1/2 + 1/4?",
            "target_concept": "finding common denominators",
            "correct_answer": "3/4",
            "common_misconceptions": [
                {
                    "wrong_answer": "2/6",
                    "type": "add_denominators_directly",
                    "explanation": "Student added numerators (1+1=2) and denominators (2+4=6) without finding a common denominator.",
                },
                {
                    "wrong_answer": "1/6",
                    "type": "denominator_multiplication_confusion",
                    "explanation": "Student multiplied denominators instead of converting to equivalent fractions.",
                },
            ],
        },
        {
            "question_id": "diag_frac_02",
            "question_text": "Calculate: 2/3 + 1/6",
            "target_concept": "equivalent fractions scaling",
            "correct_answer": "5/6",
            "common_misconceptions": [
                {
                    "wrong_answer": "3/9",
                    "type": "add_denominators_directly",
                    "explanation": "Student added across (2+1=3, 3+6=9) without converting 2/3 to 4/6.",
                },
                {
                    "wrong_answer": "1/2",
                    "type": "subtraction_sign_error",
                    "explanation": "Student subtracted instead of added (4/6 - 1/6 = 3/6 = 1/2).",
                },
            ],
        },
        {
            "question_id": "diag_frac_03",
            "question_text": "Evaluate: 3/5 + 1/2",
            "target_concept": "least common multiple (LCM 10)",
            "correct_answer": "11/10 (or 1 1/10)",
            "common_misconceptions": [
                {
                    "wrong_answer": "4/7",
                    "type": "add_denominators_directly",
                    "explanation": "Added numerators (3+1) and denominators (5+2).",
                }
            ],
        },
    ],
    "reading_comprehension_inference": [
        {
            "question_id": "diag_read_01",
            "question_text": "Read the passage: 'Marcus packed his winter coat, heavy gloves, and ice skates.' What season is it likely to be?",
            "target_concept": "textual inference",
            "correct_answer": "Winter",
            "common_misconceptions": [
                {
                    "wrong_answer": "Summer",
                    "type": "direct_literal_misread",
                    "explanation": "Student guessed without looking at clues (coat, skates).",
                }
            ],
        }
    ],
}


def generate_diagnostic_quiz(
    topic: str,
    grade_level: int = 5,
    num_questions: int = 3,
) -> Dict[str, Any]:
    """Generate a calibrated diagnostic quiz for baseline skill evaluation with guided error recovery.

    Args:
        topic: The topic key or search term (e.g. 'fractions_addition_unlike_denominators' or 'fractions').
        grade_level: Grade level target (1-12).
        num_questions: Number of questions to include (1-10).

    Returns:
        Dictionary containing quiz_id, topic, grade_level, questions, rubric, and guided recovery info.
    """
    if not isinstance(topic, str) or not topic.strip():
        return {
            "status": "error_guided_recovery",
            "error_code": "INVALID_TOPIC",
            "error_message": "Topic must be a non-empty string.",
            "guided_recovery": "Specify a learning topic such as 'fractions' or 'reading_comprehension'.",
            "available_topics": list(DIAGNOSTIC_BANK.keys()),
            "quiz_id": "quiz_fallback",
            "topic": "fractions_addition_unlike_denominators",
            "grade_level": grade_level,
            "question_count": 0,
            "questions": [],
            "rubric": {},
        }

    topic_normalized = topic.lower().replace(" ", "_").replace("-", "_")

    # Match key
    matched_key = None
    for key in DIAGNOSTIC_BANK:
        if key in topic_normalized or topic_normalized in key:
            matched_key = key
            break

    if not matched_key:
        matched_key = "fractions_addition_unlike_denominators"
        recovery_note = f"Topic '{topic}' was mapped to closest baseline bank: '{matched_key}'."
    else:
        recovery_note = "Exact diagnostic bank match found."

    questions = DIAGNOSTIC_BANK[matched_key][: max(1, min(10, num_questions))]

    return {
        "status": "success",
        "quiz_id": f"quiz_{matched_key}_gr{grade_level}",
        "topic": matched_key,
        "grade_level": grade_level,
        "question_count": len(questions),
        "questions": questions,
        "rubric": {
            "mastery_threshold": 0.8,
            "partial_threshold": 0.5,
            "diagnostic_focus": "Identify conceptual vs procedural errors and reading barriers.",
        },
        "guided_recovery": recovery_note,
    }
