"""Streamlit UI for Quiz Mentor."""

import streamlit as st

from agent.core import QuizError, generate_quiz, grade_selected_answer

st.set_page_config(page_title="Quiz Mentor", page_icon="🧠")
st.title("🧠 Quiz Mentor")
st.caption("Три вопроса по вашей теме с понятной обратной связью.")

with st.form("quiz_form"):
    topic = st.text_input("Тема", placeholder="Например: фотосинтез")
    language = st.selectbox("Язык", options=["kk", "ru", "en"], format_func=lambda x: {"kk": "Қазақша", "ru": "Русский", "en": "English"}[x])
    submitted = st.form_submit_button("Создать квиз")

if submitted:
    try:
        result = generate_quiz(topic, language)
        st.session_state.quiz = result["questions"]
        st.session_state.language = language
        st.session_state.steps = result["steps"]
        st.session_state.pop("grade", None)
    except QuizError as exc:
        st.error(str(exc))

if "quiz" in st.session_state:
    st.subheader("Квиз")
    for number, item in enumerate(st.session_state.quiz, start=1):
        st.write(f"{number}. {item['question']}")
        for option_number, option in enumerate(item["options"]):
            st.caption(f"{chr(65 + option_number)}. {option}")

    first = st.session_state.quiz[0]
    selected = st.radio("Ответьте на первый вопрос", range(4), format_func=lambda index: first["options"][index], key="selected_answer")
    if st.button("Проверить ответ"):
        try:
            graded = grade_selected_answer(first, selected, st.session_state.language)
            st.session_state.grade = graded["grade"]
            st.session_state.steps.extend(graded["steps"])
        except QuizError as exc:
            st.error(str(exc))

if "grade" in st.session_state:
    grade = st.session_state.grade
    (st.success if grade["is_correct"] else st.warning)(grade["message"])
    st.write(grade["explanation"])
    if not grade["is_correct"]:
        st.info(f"Правильный вариант: {grade['correct_option']}")

if "steps" in st.session_state:
    with st.expander("Шаги агента", expanded=True):
        for step in st.session_state.steps:
            st.write(f"**{step['name']}** — {step['detail']}")
