"""IEP Accommodations compliance validator tool with guided error recovery."""

from typing import List, Dict, Any


ACCOMMODATION_RULES = {
    "visual_scaffolding": {
        "keywords": ["diagram", "visual", "number line", "chart", "illustration", "model", "fraction bar"],
        "description": "Must include visual representations, number lines, or diagram descriptions.",
    },
    "chunked_instructions": {
        "keywords": ["step 1", "step 2", "part a", "chunk", "sub-step", "first", "next"],
        "description": "Content must be broken down into numbered discrete sub-steps.",
    },
    "high_interest_analogy": {
        "keywords": ["analogy", "like a", "imagine", "for example", "dinosaur", "space", "pizza", "lego"],
        "description": "Connects abstract concepts to student personal interests.",
    },
    "scaffolded_hinting": {
        "keywords": ["hint", "guiding question", "consider", "think about", "clue"],
        "description": "Provides tiered hints without giving direct solutions.",
    },
    "simplified_vocabulary": {
        "keywords": ["simple", "plain language", "glossary", "definition", "in other words"],
        "description": "Uses clear, grade-accessible language with explicit terminology definitions.",
    },
}


def validate_iep_accommodations(
    lesson_content: str,
    required_accommodations: List[str],
) -> Dict[str, Any]:
    """Validate that generated lesson content adheres to student IEP accommodations with guided recovery.

    Args:
        lesson_content: The text content, instructions, or exercises generated for the student.
        required_accommodations: List of accommodation keys (e.g. ['visual_scaffolding', 'chunked_instructions']).

    Returns:
        Dictionary with compliance score and guided recovery instructions for remediating missing accommodations:
            - is_compliant: Boolean flag.
            - compliance_score: Percentage score (0-100%).
            - passed_accommodations: List of satisfied accommodations.
            - missing_accommodations: List of accommodations that need remediation.
            - recommendations: Actionable fixes for missing accommodations.
            - guided_recovery: Step-by-step guidance for the agent to rewrite content to satisfy missing rules.
    """
    if not isinstance(lesson_content, str) or not lesson_content.strip():
        return {
            "status": "error_guided_recovery",
            "error_code": "EMPTY_LESSON_CONTENT",
            "error_message": "Lesson content must be a non-empty string to validate accommodations.",
            "guided_recovery": "Pass the full drafted lesson text into validate_iep_accommodations.",
            "is_compliant": False,
            "compliance_score": 0.0,
            "passed_accommodations": [],
            "missing_accommodations": required_accommodations or [],
            "recommendations": ["Provide drafted lesson content for compliance analysis."],
        }

    if not isinstance(required_accommodations, list):
        return {
            "status": "error_guided_recovery",
            "error_code": "INVALID_ACCOMMODATION_LIST",
            "error_message": "required_accommodations must be a list of strings.",
            "guided_recovery": "Provide accommodations as a list of strings, e.g. ['visual_scaffolding', 'chunked_instructions'].",
            "is_compliant": True,
            "compliance_score": 100.0,
            "passed_accommodations": [],
            "missing_accommodations": [],
            "recommendations": [],
        }

    content_lower = lesson_content.lower()
    passed = []
    missing = []
    recommendations = []

    if not required_accommodations:
        return {
            "status": "success",
            "is_compliant": True,
            "compliance_score": 100.0,
            "passed_accommodations": [],
            "missing_accommodations": [],
            "recommendations": ["No formal IEP accommodations required."],
            "guided_recovery": "All standard parameters met.",
        }

    for acc in required_accommodations:
        acc_key = acc.lower().replace(" ", "_").replace("-", "_")
        matched = False

        # Match against predefined rule sets
        for rule_key, rule in ACCOMMODATION_RULES.items():
            if rule_key in acc_key or acc_key in rule_key:
                found_keywords = [kw for kw in rule["keywords"] if kw in content_lower]
                if found_keywords:
                    passed.append(acc)
                    matched = True
                    break
                else:
                    missing.append(acc)
                    recommendations.append(
                        f"Remediation for '{acc}': {rule['description']} (Incorporate keywords/concepts: {', '.join(rule['keywords'][:3])})"
                    )
                    matched = True
                    break

        # Fallback keyword match if not in predefined map
        if not matched:
            words = [w for w in acc.lower().split() if len(w) > 3]
            if any(w in content_lower for w in words):
                passed.append(acc)
            else:
                missing.append(acc)
                recommendations.append(f"Ensure explicit inclusion of accommodation element: '{acc}'.")

    score = round((len(passed) / len(required_accommodations)) * 100.0, 1) if required_accommodations else 100.0
    is_compliant = len(missing) == 0

    guided_recovery = (
        "Content successfully satisfies all student accommodations."
        if is_compliant
        else f"To achieve 100% compliance, revise the lesson to address the {len(missing)} missing items: {', '.join(missing)}."
    )

    return {
        "status": "success" if is_compliant else "needs_remediation",
        "is_compliant": is_compliant,
        "compliance_score": score,
        "passed_accommodations": passed,
        "missing_accommodations": missing,
        "recommendations": recommendations,
        "guided_recovery": guided_recovery,
    }
