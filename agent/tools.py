"""Deterministic tools and their OpenAI function schemas."""

from __future__ import annotations

import re
from typing import Any


PUBLISH_QUIZ_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "publish_quiz",
        "description": "Publish the three generated quiz questions for the student.",
        "parameters": {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "options": {
                                "type": "array",
                                "minItems": 4,
                                "maxItems": 4,
                                "items": {"type": "string"},
                            },
                            "correct_index": {"type": "integer", "minimum": 0, "maximum": 3},
                            "explanation": {"type": "string"},
                        },
                        "required": ["question", "options", "correct_index", "explanation"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["questions"],
            "additionalProperties": False,
        },
    },
}


def publish_quiz(questions: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate the model's proposed quiz and return a small tool result."""
    if len(questions) != 3:
        raise ValueError("Нужно ровно три вопроса.")
    cleaned: list[dict[str, Any]] = []
    for item in questions:
        question = str(item.get("question", "")).strip()
        options = item.get("options", [])
        explanation = str(item.get("explanation", "")).strip()
        correct_index = item.get("correct_index")
        if not question or not explanation or not isinstance(options, list) or len(options) != 4:
            raise ValueError("Каждый вопрос должен содержать текст, 4 варианта и объяснение.")
        if not isinstance(correct_index, int) or correct_index not in range(4):
            raise ValueError("Некорректный индекс правильного ответа.")
        cleaned.append(
            {
                "question": question,
                "options": [str(option).strip() for option in options],
                "correct_index": correct_index,
                "explanation": explanation,
            }
        )
    return {"questions": cleaned, "count": len(cleaned)}


def grade_answer(question: dict[str, Any], selected_index: int, language: str) -> dict[str, Any]:
    """Grade a selected option deterministically and return localized feedback."""
    if selected_index not in range(len(question["options"])):
        raise ValueError("Выберите один из предложенных вариантов.")
    correct = selected_index == question["correct_index"]
    labels = {
        "kk": ("Дұрыс!", "Әзірше дұрыс емес."),
        "ru": ("Верно!", "Пока неверно."),
        "en": ("Correct!", "Not quite."),
    }
    positive, negative = labels[language]
    return {
        "is_correct": correct,
        "message": positive if correct else negative,
        "explanation": question["explanation"],
        "correct_option": question["options"][question["correct_index"]],
    }
