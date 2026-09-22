import json
from types import SimpleNamespace

import pytest

from agent.core import QuizError, generate_quiz, grade_selected_answer


def fake_client():
    questions = [
        {"question": f"Question {i}", "options": ["A", "B", "C", "D"], "correct_index": 1, "explanation": "Because B is correct."}
        for i in range(1, 4)
    ]
    call = SimpleNamespace(function=SimpleNamespace(name="publish_quiz", arguments=json.dumps({"questions": questions})))
    message = SimpleNamespace(tool_calls=[call])
    response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **_: response)))


def test_openai_tool_call_generates_valid_quiz():
    result = generate_quiz("photosynthesis", "en", client=fake_client())
    assert len(result["questions"]) == 3
    assert result["questions"][0]["correct_index"] == 1
    assert any(step["name"] == "Инструмент: publish_quiz" for step in result["steps"])


def test_invalid_request_and_answer_are_friendly():
    with pytest.raises(QuizError, match="Введите тему"):
        generate_quiz("  ", "ru", client=fake_client())
    malformed = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[]))]
                )
            )
        )
    )
    with pytest.raises(QuizError, match="не вернула квиз"):
        generate_quiz("biology", "en", client=malformed)
    question = {"options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "Test explanation."}
    result = grade_selected_answer(question, 3, "en")
    assert result["grade"]["is_correct"] is False
    assert result["grade"]["correct_option"] == "A"
