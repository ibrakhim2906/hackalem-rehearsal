"""OpenAI tool-calling loop for quiz generation and deterministic grading."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

from agent.prompts import LANGUAGE_NAMES, QUIZ_SYSTEM_PROMPT
from agent.tools import PUBLISH_QUIZ_SCHEMA, grade_answer, publish_quiz

load_dotenv()

MAX_TOPIC_LENGTH = 160


class QuizError(Exception):
    """A friendly, expected error that the UI can display."""


def validate_request(topic: str, language: str) -> tuple[str, str]:
    topic = topic.strip()
    if not topic:
        raise QuizError("Введите тему для квиза.")
    if len(topic) > MAX_TOPIC_LENGTH:
        raise QuizError(f"Тема слишком длинная: максимум {MAX_TOPIC_LENGTH} символов.")
    if language not in LANGUAGE_NAMES:
        raise QuizError("Выберите язык kk, ru или en.")
    return topic, language


def _step(name: str, detail: str) -> dict[str, str]:
    return {"name": name, "detail": detail}


def _client() -> Any:
    from openai import OpenAI

    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_quiz(topic: str, language: str, client: Any | None = None) -> dict[str, Any]:
    """Ask OpenAI to call publish_quiz, returning the validated quiz and step log."""
    topic, language = validate_request(topic, language)
    if not os.getenv("OPENAI_API_KEY") and client is None:
        raise QuizError("OPENAI_API_KEY не найден. Добавьте ключ в .env и перезапустите приложение.")

    steps = [_step("План", f"Создаю квиз по теме «{topic}» на языке {language}.")]
    try:
        response = (client or _client()).chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {topic}\nLanguage: {LANGUAGE_NAMES[language]}"},
            ],
            tools=[PUBLISH_QUIZ_SCHEMA],
            tool_choice={"type": "function", "function": {"name": "publish_quiz"}},
        )
        calls = response.choices[0].message.tool_calls or []
        call = next((item for item in calls if item.function.name == "publish_quiz"), None)
        if call is None:
            raise QuizError("Модель не вернула квиз через инструмент. Попробуйте ещё раз.")
        arguments = json.loads(call.function.arguments)
        result = publish_quiz(arguments["questions"])
        steps.append(_step("Инструмент: publish_quiz", "Проверены и сохранены 3 вопроса."))
        steps.append(_step("Проверка", "Формат: 3 вопроса, по 4 варианта, правильные ответы заданы."))
        return {"questions": result["questions"], "steps": steps}
    except QuizError:
        raise
    except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as exc:
        raise QuizError(f"Не удалось обработать ответ модели: {exc}") from exc
    except Exception as exc:
        raise QuizError(f"Ошибка при обращении к OpenAI: {exc}") from exc


def grade_selected_answer(question: dict[str, Any], selected_index: int, language: str) -> dict[str, Any]:
    if language not in LANGUAGE_NAMES:
        raise QuizError("Выберите язык kk, ru или en.")
    try:
        result = grade_answer(question, selected_index, language)
        return {"grade": result, "steps": [_step("Инструмент: grade_answer", "Сверен выбранный вариант с правильным ответом."), _step("Проверка", "Добавлено объяснение результата.")]}
    except (KeyError, TypeError, ValueError) as exc:
        raise QuizError(str(exc)) from exc
