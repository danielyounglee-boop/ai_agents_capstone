"""Educational standards lookup and prerequisite tree mapping tool with guided error recovery."""

from typing import List, Dict, Any, Optional

# Core Standards Knowledge Base (Common Core Math & ELA benchmarks)
CURRICULUM_STANDARDS: List[Dict[str, Any]] = [
    {
        "code": "CCSS.MATH.CONTENT.3.NF.A.1",
        "subject": "Mathematics",
        "grade_level": 3,
        "topic": "fractions",
        "title": "Understand a fraction as a number on the number line",
        "description": "Understand a fraction 1/b as the quantity formed by 1 part when a whole is partitioned into b equal parts.",
        "prerequisites": ["equal_sharing", "whole_numbers"],
        "key_vocabulary": ["numerator", "denominator", "partition", "unit fraction"],
    },
    {
        "code": "CCSS.MATH.CONTENT.4.NF.A.1",
        "subject": "Mathematics",
        "grade_level": 4,
        "topic": "fractions",
        "title": "Explain fraction equivalence",
        "description": "Explain why a fraction a/b is equivalent to a fraction (n*a)/(n*b) by using visual fraction models.",
        "prerequisites": ["CCSS.MATH.CONTENT.3.NF.A.1", "multiplication_facts"],
        "key_vocabulary": ["equivalent", "common factor", "simplify"],
    },
    {
        "code": "CCSS.MATH.CONTENT.5.NF.A.1",
        "subject": "Mathematics",
        "grade_level": 5,
        "topic": "fractions",
        "title": "Add and subtract fractions with unlike denominators",
        "description": "Add and subtract fractions with unlike denominators by replacing given fractions with equivalent fractions with like denominators.",
        "prerequisites": ["CCSS.MATH.CONTENT.4.NF.A.1", "least_common_multiple"],
        "key_vocabulary": ["common denominator", "least common multiple", "sum", "difference"],
    },
    {
        "code": "CCSS.MATH.CONTENT.6.NS.A.1",
        "subject": "Mathematics",
        "grade_level": 6,
        "topic": "fractions",
        "title": "Divide fractions by fractions",
        "description": "Interpret and compute quotients of fractions, and solve word problems involving division of fractions by fractions.",
        "prerequisites": ["CCSS.MATH.CONTENT.5.NF.A.1", "reciprocal"],
        "key_vocabulary": ["reciprocal", "quotient", "inverse operation"],
    },
    {
        "code": "CCSS.ELA-LITERACY.RL.4.1",
        "subject": "English Language Arts",
        "grade_level": 4,
        "topic": "reading_comprehension",
        "title": "Refer to details and examples in a text",
        "description": "Refer to details and examples in a text when explaining what the text says explicitly and when drawing inferences.",
        "prerequisites": ["basic_inference", "sentence_structure"],
        "key_vocabulary": ["explicit", "inference", "evidence"],
    },
    {
        "code": "CCSS.ELA-LITERACY.RL.5.1",
        "subject": "English Language Arts",
        "grade_level": 5,
        "topic": "reading_comprehension",
        "title": "Quote accurately from a text",
        "description": "Quote accurately from a text when explaining what the text says explicitly and when drawing inferences from the text.",
        "prerequisites": ["CCSS.ELA-LITERACY.RL.4.1", "quotation_marks"],
        "key_vocabulary": ["quote", "textual evidence", "analysis"],
    },
]


def lookup_educational_standards(
    grade_level: Optional[int] = None,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    keyword: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search and retrieve curriculum standards by grade, subject, topic, or keyword with guided recovery.

    Args:
        grade_level: Target grade level (1-12).
        subject: Subject area e.g. 'Mathematics' or 'English Language Arts'.
        topic: Specific learning domain e.g. 'fractions', 'geometry', 'reading_comprehension'.
        keyword: Free-text search across titles and descriptions.

    Returns:
        List of matching standard definitions, or a guided error recovery object if no match found.
    """
    # Parameter sanity checks
    if grade_level is not None and (not isinstance(grade_level, int) or grade_level < 1 or grade_level > 12):
        return [
            {
                "status": "error_guided_recovery",
                "error_code": "INVALID_GRADE_LEVEL",
                "error_message": f"Grade level {grade_level} is invalid. Supported grades are 1 through 12.",
                "guided_recovery": "Please specify an integer grade level between 1 and 12 (e.g. grade_level=5 for 5th grade).",
                "available_grades": [3, 4, 5, 6],
            }
        ]

    results = []
    for standard in CURRICULUM_STANDARDS:
        if grade_level is not None and standard["grade_level"] != grade_level:
            continue
        if subject is not None and subject.lower() not in standard["subject"].lower():
            continue
        if topic is not None and topic.lower() not in standard["topic"].lower():
            continue
        if keyword is not None:
            kw = keyword.lower()
            text_corpus = f"{standard['code']} {standard['title']} {standard['description']} {' '.join(standard['key_vocabulary'])}".lower()
            if kw not in text_corpus:
                continue
        results.append(standard)

    # Fallback to closest subject/topic if no strict match
    if not results and (subject or topic):
        for standard in CURRICULUM_STANDARDS:
            if (subject and subject.lower() in standard["subject"].lower()) or (topic and topic.lower() in standard["topic"].lower()):
                results.append(standard)

    # Guided Recovery if still empty
    if not results:
        return [
            {
                "status": "error_guided_recovery",
                "error_code": "NO_STANDARDS_FOUND",
                "error_message": f"No curriculum standards found matching criteria (grade={grade_level}, subject='{subject}', topic='{topic}', keyword='{keyword}').",
                "guided_recovery": "Try searching with topic='fractions' or topic='reading_comprehension', or omitting the keyword filter.",
                "available_topics": ["fractions", "reading_comprehension"],
                "available_grades": [3, 4, 5, 6],
            }
        ]

    return results
