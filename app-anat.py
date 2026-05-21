import streamlit as st
import pdfplumber
import re

st.title("📚 Анат Test Trainer")

# ---------- PARSER ----------
text = ""

with pdfplumber.open("тести анат.pdf") as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

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


import ipywidgets as widgets
from IPython.display import display, clear_output
import random

random.shuffle(tests)

score = 0
current_question = 0

def show_question():

    clear_output(wait=True)

    global current_question

    if current_question >= len(tests):
        print("Тест завершён!")
        print(f"Результат: {score}/{len(tests)}")
        return

    test = tests[current_question]

    print(test["question"])
    print()

    for option in test["options"]:

        btn = widgets.Button(
            description=option,
            layout=widgets.Layout(width='600px')
        )

        btn.on_click(lambda b, opt=option: check_answer(opt))

        display(btn)

def check_answer(selected):

    global score, current_question

    test = tests[current_question]
    correct = test["answer"]

    clear_output(wait=True)

    # Вопрос
    question_html = widgets.HTML(
        f"<h3>{test['question']}</h3>"
    )

    display(question_html)

    # Ответы
    for option in test["options"]:

        # Правильный ответ
        if option == correct:
            style = "success"

        # Неправильный выбранный
        elif option == selected:
            style = "danger"

        else:
            style = ""

        button = widgets.Button(
            description=option,
            disabled=True,
            button_style=style,
            layout=widgets.Layout(width='400px')
        )

        display(button)

    # Текст результата
    if selected == correct:
        display(widgets.HTML(
            "<h3 style='color:green;'>✅ Правильно!</h3>"
        ))
        score += 1
    else:
        display(widgets.HTML(
            f"<h3 style='color:red;'>❌ Неправильно</h3>"
            f"<p>Правильный ответ: <b>{correct}</b></p>"
        ))

    # Кнопка дальше
    next_button = widgets.Button(
        description="Дальше",
        button_style="info",
        layout=widgets.Layout(width='200px')
    )

    def next_question(b):
        global current_question

        current_question += 1
        show_question()

    next_button.on_click(next_question)

    display(next_button)


show_question()
