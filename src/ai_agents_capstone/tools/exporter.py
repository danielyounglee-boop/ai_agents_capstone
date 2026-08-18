"""Curriculum and IEP progress report exporter tool."""

import json
import os
from typing import Dict, Any, Optional


def export_lesson_plan(
    lesson_data: Dict[str, Any],
    output_dir: str = "data/lessons",
    filename: Optional[str] = None,
) -> str:
    """Export a synthesized lesson plan to a formatted Markdown and JSON artifact.

    Args:
        lesson_data: Dictionary representing the synthesized lesson plan.
        output_dir: Directory to save exported files.
        filename: Optional custom file basename without extension.

    Returns:
        Absolute filepath to the exported markdown lesson plan.
    """
    os.makedirs(output_dir, exist_ok=True)
    lesson_id = lesson_data.get("lesson_id", "lesson_plan")
    base_name = filename or f"{lesson_id}"
    md_path = os.path.join(output_dir, f"{base_name}.md")
    json_path = os.path.join(output_dir, f"{base_name}.json")

    # Save JSON raw
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(lesson_data, f, indent=2, default=str)

    # Format Markdown
    title = lesson_data.get("title", "Personalized Adaptive Lesson Plan")
    student_id = lesson_data.get("student_id", "Student")
    target_skill = lesson_data.get("target_skill", "Target Skill")
    reading_level = lesson_data.get("target_reading_level", "N/A")
    standards = lesson_data.get("aligned_standards", [])
    sections = lesson_data.get("sections", [])
    practice = lesson_data.get("practice_exercises", [])
    educator_notes = lesson_data.get("educator_notes", "")

    md_lines = [
        f"# 📚 {title}",
        f"**Student ID:** `{student_id}` | **Target Skill:** {target_skill} | **Target Reading Grade Level:** {reading_level}",
        "",
        "## 🎯 Aligned Educational Standards",
    ]

    for std in standards:
        if isinstance(std, dict):
            md_lines.append(f"- **{std.get('code', 'Standard')}:** {std.get('description', '')}")
        else:
            md_lines.append(f"- {std}")

    md_lines.append("\n## 📖 Personalized Lesson Sections\n")
    for idx, sec in enumerate(sections, 1):
        if isinstance(sec, dict):
            sec_title = sec.get("title", f"Section {idx}")
            sec_content = sec.get("content", "")
            accommodations = sec.get("applied_accommodations", [])
            theme = sec.get("analogy_or_theme", "")
            cfu = sec.get("check_for_understanding_question", "")

            md_lines.append(f"### {idx}. {sec_title}")
            if theme:
                md_lines.append(f"> 💡 **High-Interest Analogy:** *{theme}*")
            if accommodations:
                md_lines.append(f"> ♿ **Accommodations Applied:** {', '.join(accommodations)}")
            md_lines.append(f"\n{sec_content}\n")
            if cfu:
                md_lines.append(f"**Check for Understanding:** {cfu}\n")

    md_lines.append("\n## ✏️ Scaffolded Practice Exercises\n")
    for idx, ex in enumerate(practice, 1):
        if isinstance(ex, dict):
            prompt = ex.get("prompt", "")
            diff = ex.get("difficulty_level", "standard")
            t1 = ex.get("hint_tier_1_concept", "")
            t2 = ex.get("hint_tier_2_strategy", "")
            t3 = ex.get("hint_tier_3_substep", "")
            ans = ex.get("solution_key", "")

            md_lines.append(f"#### Problem {idx} ({diff.title()} Tier)")
            md_lines.append(f"**Problem:** {prompt}\n")
            md_lines.append("<details><summary>🔍 Socratic Hints & Solution</summary>\n")
            md_lines.append(f"- **Tier 1 (Guiding Question):** {t1}")
            md_lines.append(f"- **Tier 2 (Strategy Clue):** {t2}")
            md_lines.append(f"- **Tier 3 (Worked Sub-Step):** {t3}")
            md_lines.append(f"- **Final Solution Key:** `{ans}`")
            md_lines.append("</details>\n")

    if educator_notes:
        md_lines.append("\n## 👩‍🏫 Educator / IEP Specialist Notes\n")
        md_lines.append(educator_notes)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return os.path.abspath(md_path)
