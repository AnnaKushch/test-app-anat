import streamlit as st
import pdfplumber
import re
import random

st.set_page_config(page_title="Anatomy Test", layout="centered")

FILE_PATH = "тести анат.pdf"


# ---------- LOAD PDF ----------
@st.cache_data
def load_pdf():
    with pdfplumber.open(FILE_PATH) as pdf:
        text = ""
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text


# ---------- PARSER ----------
@st.cache_data
def parse_tests(text):

    text = text.replace("\xa0", " ")

    text = text.replace("А)", "A)")
    text = text.replace("В)", "B)")
    text = text.replace("С)", "C)")

    blocks = re.split(r"\n?\d+\.\s", text)

    tests = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        question = re.split(r"[A-E]\)", block)[0].strip()
        options = re.findall(r"[A-E]\)\s*(.*?)(?=(?:[A-E]\)|$))", block, re.S)
        options = [o.replace("\n", " ").strip() for o in options]

        if len(options) >= 4:

            correct = options[0]   # сначала запоминаем правильный
        
            random.shuffle(options)  # потом перемешиваем
        
            tests.append({
                "question": question,
                "options": options,
                "answer": correct
            })

    return tests


# ---------- INIT STATE ----------
if "started" not in st.session_state:
    st.session_state.started = False

if "mode" not in st.session_state:
    st.session_state.mode = None

if "i" not in st.session_state:
    st.session_state.i = 0

if "checked" not in st.session_state:
    st.session_state.checked = False

if "selected" not in st.session_state:
    st.session_state.selected = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "results" not in st.session_state:
    st.session_state.results = []


# ---------- LOAD DATA ----------
text = load_pdf()
tests = parse_tests(text)

if st.session_state.get("finished", False):

    st.success("🎉 Тест завершён!")

    st.write(f"Результат: {st.session_state.score} / {len(st.session_state.exam_tests)}")

    if st.button("🔄 Начать заново"):

        st.session_state.started = False
        st.session_state.finished = False
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.results = []

        st.rerun()

    st.stop()


# ---------- HOME ----------
if not st.session_state.started:

    st.title("📚 Anatomy Trainer")

    mode = st.radio(
        "Режим теста",
        ["🔀 Случайный (50 вопросов)", "📖 По порядку (все вопросы)"]
    )

    if st.button("▶ Начать"):

        st.session_state.started = True
        st.session_state.mode = mode
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.checked = False
        st.session_state.selected = None
        st.session_state.results = []

        # ---------- MODE LOGIC ----------
        if mode == "📖 По порядку (все вопросы)":
            st.session_state.exam_tests = tests
        else:
            st.session_state.exam_tests = random.sample(
                tests,
                min(50, len(tests))
            )

        st.rerun()

    st.stop()


# ---------- CURRENT QUESTION ----------
i = st.session_state.i
# 🔥 защита от выхода за границы
if i >= len(st.session_state.exam_tests):
    st.session_state.finished = True
    st.rerun()

test = st.session_state.exam_tests[i]


st.write(f"### Вопрос {i + 1} / {len(st.session_state.exam_tests)}")
st.write(test["question"])


# ---------- ANSWER ----------
if not st.session_state.checked:

    st.session_state.selected = st.radio(
        "Выбери ответ",
        test["options"],
        key=f"q_{i}"
    )

    if st.button("Ответить"):

        st.session_state.checked = True

        is_correct = st.session_state.selected == test["answer"]

        if is_correct:
            st.session_state.score += 1

        st.session_state.results.append({
            "question": test["question"],
            "options": test["options"],
            "selected": st.session_state.selected,
            "correct": test["answer"],
            "is_correct": is_correct
        })

        st.rerun()


# ---------- RESULT ----------
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

    if st.session_state.selected == correct:
        st.success("✅ Правильно")
    else:
        st.error(f"❌ Неправильно. Правильный: {correct}")

    if st.button("Далее ➡️"):

        st.session_state.i += 1
        st.session_state.checked = False
        st.session_state.selected = None

        if st.session_state.i >= len(st.session_state.exam_tests):
            st.session_state.finished = True
            st.rerun()

        st.rerun()


# ---------- NAVIGATION ----------
st.markdown("---")
st.markdown("### 📍 Навигация")

cols = st.columns(5)

if "exam_tests" in st.session_state:

    cols = st.columns(5)

    for idx in range(len(st.session_state.exam_tests)):

        col = cols[idx % 5]
    
        with col:
    
            label = str(idx + 1)
    
            if idx < len(st.session_state.results):
    
                if st.session_state.results[idx]["is_correct"]:
                    label = "🟢 " + label
                else:
                    label = "🔴 " + label
            else:
                label = "⚪ " + label
    
            if st.button(label, key=f"nav_{idx}"):
    
                st.session_state.i = idx
                st.session_state.checked = False
                st.session_state.selected = None
                st.rerun()
