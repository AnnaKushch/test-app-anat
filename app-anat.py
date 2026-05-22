import streamlit as st
import pdfplumber
import re
import random

st.set_page_config(page_title="Test Trainer", layout="centered")

st.title("📚 Medical Test Trainer")


# ---------- LOAD PDF ----------
@st.cache_data
def load_pdf():
    with pdfplumber.open("тести анат.pdf") as pdf:
        text = ""
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text


# ---------- PARSER (твоя логика) ----------
@st.cache_data
def parse_tests(text):

    text_clean = text.replace("\xa0", " ")

    # 🔥 заменяем кириллическую А на латинскую A
    text_clean = text_clean.replace("А)", "A)")
    text_clean = text_clean.replace("В)", "B)")
    text_clean = text_clean.replace("С)", "C)")
    text_clean = text_clean.replace("D)", "D)")
    text_clean = text_clean.replace("E)", "E)")
    
    blocks = re.split(r"\n?\d+\.\s", text_clean)
    
    tests = []

    for block in blocks:
    
        block = block.strip()
        if not block:
            continue
    
        # вопрос = всё до первого варианта
        question = re.split(r"[A-E]\)", block)[0].strip()
    
        # варианты
        options = re.findall(r"[A-E]\)\s*(.*?)(?=(?:[A-E]\)|$))", block, re.S)
    
        options = [o.replace("\n", " ").strip().rstrip(";") for o in options]
    
        if len(options) >= 4:
            tests.append({
                "question": question,
                "options": options,
                "answer": options[0]
            })

    return tests


# ---------- INIT ----------
if "i" not in st.session_state:
    st.session_state.i = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "checked" not in st.session_state:
    st.session_state.checked = False

if "selected" not in st.session_state:
    st.session_state.selected = None

if "counted" not in st.session_state:
    st.session_state.counted = False

if "saved_answer" not in st.session_state:
    st.session_state.saved_answer = False


# ---------- LOAD ----------
text = load_pdf()
parsed_tests = parse_tests(text)

# все тесты
if "tests" not in st.session_state:

    random.shuffle(parsed_tests)

    st.session_state.tests = parsed_tests


# экзамен 50 вопросов
if "exam_tests" not in st.session_state:

    st.session_state.exam_tests = random.sample(
        st.session_state.tests,
        50
    )


# результаты
if "results" not in st.session_state:
    st.session_state.results = []


tests = st.session_state.exam_tests

# ---------- SHOW OPTIONS ----------
i = st.session_state.i
test = tests[i]
correct = test["answer"]

if st.session_state.get("checked", False) is False:

    for opt in test["options"]:

        if st.button(opt, key=f"{i}_{opt}"):

            st.session_state.selected = opt
            st.session_state.checked = True
            st.rerun()


# ---------- SHOW RESULT ----------
else:

    correct = test["answer"]

    st.write("---")

    for opt in test["options"]:

        if opt == correct:
            st.markdown("🟢 " + opt)

        elif opt == st.session_state.selected:
            st.markdown("🔴 " + opt)

        else:
            st.markdown("⚪ " + opt)

    # ---------- SCORE ----------
    # сохраняем результат вопроса
if not st.session_state.get("saved_answer", False):

    st.session_state.results.append({
        "question": test["question"],
        "selected": st.session_state.selected,
        "correct": correct,
        "is_correct": st.session_state.selected == correct
    })

    st.session_state.saved_answer = True
    
    if st.session_state.selected == correct:
        st.success("✅ Правильно")

        # защита от двойного подсчёта
        if not st.session_state.get("counted", False):
            st.session_state.score += 1
            st.session_state.counted = True

    else:
        st.error(f"❌ Неправильно. Правильный: {correct}")

    # ---------- NEXT ----------
    if st.button("Дальше ➡️"):

        st.session_state.i += 1
        st.session_state.checked = False
        st.session_state.selected = None
        st.session_state.counted = False
        st.session_state.saved_answer = False
    
        st.rerun()

# ---------- FINISH CHECK ----------
if st.session_state.i >= 50:

    st.success("🎉 Экзамен завершён!")

    correct_answers = sum(
        r["is_correct"]
        for r in st.session_state.results
    )

    st.write(f"Результат: {correct_answers}/50")

    st.write("---")
    st.header("📋 Разбор ошибок")

    for idx, r in enumerate(st.session_state.results, start=1):

        if r["is_correct"]:
            st.markdown(f"### {idx}. ✅")
        else:
            st.markdown(f"### {idx}. ❌")

        st.write(r["question"])

        st.markdown(f"**Твой ответ:** {r['selected']}")
        st.markdown(f"**Правильный ответ:** 🟢 {r['correct']}")

        st.write("---")


    if st.button("🔄 Начать заново"):

        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.checked = False
        st.session_state.selected = None
        st.session_state.counted = False
        st.session_state.saved_answer = False

        st.session_state.results = []

        st.session_state.exam_tests = random.sample(
            st.session_state.tests,
            50
        )

        st.rerun()

    st.stop()


# ---------- CURRENT QUESTION ----------
i = st.session_state.i
test = tests[i]

st.write(f"Вопрос {i+1} из 50")

st.subheader(test["question"])
