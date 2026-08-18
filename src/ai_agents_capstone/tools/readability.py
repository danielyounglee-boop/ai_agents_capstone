"""Readability and Lexile analyzer tool for educational text adaptation."""

import re
from typing import Dict, Any


def count_syllables(word: str) -> int:
    """Estimate syllable count in an English word using phonetic heuristics."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1

    # Remove silent 'e' at the end
    if word.endswith("e") and not word.endswith("le"):
        word = word[:-1]

    # Find vowel groups
    vowels = "aeiouy"
    count = len(re.findall(r"[aeiouy]+", word))
    return max(1, count)


def analyze_readability(text: str) -> Dict[str, Any]:
    """Calculate Flesch-Kincaid Grade Level, Reading Ease, and Lexile estimate for text.

    Args:
        text: The raw educational text, explanation, or problem prompt to analyze.

    Returns:
        Dictionary with:
            - word_count: Total words.
            - sentence_count: Total sentences.
            - syllable_count: Total syllables.
            - flesch_reading_ease: Score (0-100, where higher is easier).
            - flesch_kincaid_grade_level: Usable grade level (e.g. 5.2).
            - estimated_lexile: Estimated Lexile measure (e.g. '750L').
            - reading_difficulty_band: 'Elementary (1-5)', 'Middle (6-8)', 'High (9-12)', 'College'.
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "syllable_count": 0,
            "flesch_reading_ease": 100.0,
            "flesch_kincaid_grade_level": 0.0,
            "estimated_lexile": "BR",
            "reading_difficulty_band": "Elementary (1-5)",
        }

    # Split sentences (split on ., !, ?, or newlines)
    sentences = [s.strip() for s in re.split(r"[.!?]+|\n+", cleaned_text) if s.strip()]
    sentence_count = max(1, len(sentences))

    # Split words
    words = [w.strip() for w in re.findall(r"\b[A-Za-z0-9'-]+\b", cleaned_text) if w.strip()]
    word_count = max(1, len(words))

    # Count syllables
    syllable_count = sum(count_syllables(w) for w in words)

    # Standard Flesch Formulas
    # Flesch Reading Ease = 206.835 - 1.015 * (total words / total sentences) - 84.6 * (total syllables / total words)
    words_per_sentence = word_count / sentence_count
    syllables_per_word = syllable_count / word_count

    reading_ease = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
    reading_ease = round(max(0.0, min(100.0, reading_ease)), 1)

    # Flesch-Kincaid Grade Level = 0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
    fk_grade = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59
    fk_grade = round(max(0.5, fk_grade), 1)

    # Lexile Conversion Approximation: Lexile ~= (FK Grade Level * 125) + 150
    lexile_val = int(max(0, (fk_grade * 125) + 150))
    estimated_lexile = f"{lexile_val}L" if lexile_val > 0 else "BR (Beginning Reader)"

    if fk_grade <= 5.5:
        band = "Elementary (Grade 1-5)"
    elif fk_grade <= 8.5:
        band = "Middle School (Grade 6-8)"
    elif fk_grade <= 12.0:
        band = "High School (Grade 9-12)"
    else:
        band = "College / Advanced"

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "syllable_count": syllable_count,
        "flesch_reading_ease": reading_ease,
        "flesch_kincaid_grade_level": fk_grade,
        "estimated_lexile": estimated_lexile,
        "reading_difficulty_band": band,
    }
