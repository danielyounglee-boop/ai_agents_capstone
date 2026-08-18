"""IEP Accommodations compliance validator tool."""

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
    """Validate that generated lesson content or practice set adheres to a student's IEP accommodations.

    Args:
        lesson_content: The text content, instructions, or exercises generated for the student.
        required_accommodations: List of accommodation keys or descriptions (e.g. ['visual_scaffolding', 'chunked_instructions']).

    Returns:
        Dictionary with:
            - is_compliant: Boolean flag.
            - compliance_score: Percentage score (0-100%).
            - passed_accommodations: List of satisfied accommodations.
            - missing_accommodations: List of accommodations that need remediation.
            - recommendations: Actionable fixes for missing accommodations.
    """
    content_lower = lesson_content.lower()
    passed = []
    missing = []
    recommendations = []

    if not required_accommodations:
        return {
            "is_compliant": True,
            "compliance_score": 100.0,
            "passed_accommodations": [],
            "missing_accommodations": [],
            "recommendations": ["No formal IEP accommodations required."],
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
                        f"Missing '{acc}': {rule['description']} (Add elements like: {', '.join(rule['keywords'][:3])})"
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
                recommendations.append(f"Ensure explicit application of accommodation: '{acc}'.")

    score = round((len(passed) / len(required_accommodations)) * 100.0, 1) if required_accommodations else 100.0
    is_compliant = len(missing) == 0

    return {
        "is_compliant": is_compliant,
        "compliance_score": score,
        "passed_accommodations": passed,
        "missing_accommodations": missing,
        "recommendations": recommendations,
    }
