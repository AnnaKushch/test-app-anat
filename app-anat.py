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
    st.session_state.score = 0
    st.session_state.checked = False
    st.session_state.selected = None


# ---------- LOAD ON START ----------
text = load_pdf()
tests = parse_tests(text)

if "shuffled" not in st.session_state:
    random.shuffle(tests)
    st.session_state.shuffled = True

random.shuffle(tests) 

st.write("Готово тестов:", len(tests))


# ---------- CURRENT TEST ----------
i = st.session_state.i
test = tests[i]

st.subheader(test["question"])

# ---------- ANSWER SELECTION ----------
for opt in test["options"]:
    if st.button(opt, key=opt):

        st.session_state.selected = opt
        st.session_state.checked = True


# ---------- CHECK RESULT ----------
if st.session_state.get("checked", False):

    correct = test["answer"]

    st.write("---")

    for opt in test["options"]:

        if opt == correct:
            st.markdown("🟢 " + opt)

        elif opt == st.session_state.selected:
            st.markdown("🔴 " + opt)

        else:
            st.markdown("⚪ " + opt)

    # ---------- TEXT FEEDBACK ----------
    if st.session_state.selected == correct:
        st.success("✅ Правильно")
        st.session_state.score += 1
    else:
        st.error(f"❌ Неправильно. Правильный ответ: {correct}")


    # ---------- NEXT BUTTON ----------
    if st.button("Дальше ➡️"):

        st.session_state.i += 1
        st.session_state.checked = False
        st.session_state.selected = None
        st.rerun()


