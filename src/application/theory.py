import os
import re
import json
from tkinter import *
from mk_scrollable_frame import mkscframe, bind_all_children
from tkinter import messagebox

THEORY_DIR = os.path.join('..','..','data','theory_tests_dir')

main_theory_frame = None

def show_theory_section(m_theory_frame):
    global main_theory_frame
    main_theory_frame = m_theory_frame
    main_theory_frame.place(relx=0.15, rely=0, relwidth=0.85, relheight=1)

    scrollable_frame, scrollbar, canvas = mkscframe(main_theory_frame)

    if not os.path.exists(THEORY_DIR):
        Label(scrollable_frame, text="Папка не найдена", fg="red", bg="white").pack(pady=20)
        bind_all_children(scrollable_frame, scrollbar, canvas)
        return

    try:
        modules = [m for m in os.listdir(THEORY_DIR) if os.path.isdir(os.path.join(THEORY_DIR, m))]
    except Exception as e: # <- ПРОВЕРКА НА МОДУЛИ И ТЕМЫ
        Label(scrollable_frame, text=f"Ошибка: {e}", fg="red").pack(pady=20)
        bind_all_children(scrollable_frame, scrollbar, canvas)
        return

    def natural_sort_key(name):
        parts = re.split(r'(\d+)', name)
        for i, part in enumerate(parts):
            if part.isdigit():
                parts[i] = int(part)
        return parts

    # Сортируем модули естественным образом
    for module in sorted(modules, key=natural_sort_key):
        module_path = os.path.join(THEORY_DIR, module)
        # Заголовок модуля — как в меню, но чуть темнее
        s = Label(scrollable_frame, text=module, bg='#c8c8c8', font=('Arial', 16, 'bold'), anchor='w')
        s.pack(fill='x', padx=15, pady=(20,5))

        try:
            all_items = os.listdir(module_path)
            themes = [t for t in all_items if os.path.isdir(os.path.join(module_path, t))]
        except OSError:
            themes = []

        # Сортируем ТЕМЫ естественным образом
        for theme in sorted(themes, key=natural_sort_key):
            theme_full_path = os.path.join(module_path, theme)
            t = Button(
                scrollable_frame,
                text=theme,
                bg='#e0e0e0',
                fg='#222222',
                activebackground='#c0c0c0',
                activeforeground='#222222',
                font=('Arial', 13),
                anchor='w',
                bd=0,
                relief='flat'
            )
            # Чтобы theme и theme_full_path корректно захватывались
            t.config(command=lambda tfp=theme_full_path, tname=theme: show_theme_file(tfp, tname))
            t.pack(fill='x', padx=(45,15), pady=5)  # отступы как в коде

    bind_all_children(scrollable_frame, scrollbar, canvas)

def show_theme_file(theme_folder_path, name):
    global main_theory_frame
    theme_frame = Frame(main_theory_frame, bg='white')
    theme_frame.place(relwidth=1, relheight=1)

    # Заголовок
    title_frame = Frame(theme_frame, bg='#c8c8c8')
    title_frame.pack(fill='x', padx=0, pady=(0,10))
    btn_back = Button(title_frame,
                      text="← Назад",
                      command=lambda: theme_frame.destroy(),
                      font=('Arial', 12, 'bold'),
                      bg='#e0e0e0',
                      fg='#222222',
                      activebackground='#c0c0c0',
                      activeforeground='#222222',
                      bd=0,
                      relief='flat')
    btn_back.pack(side='left', padx=10, pady=10)
    title = Label(title_frame, text=name, bg='#c8c8c8', font=('', 24), anchor='w')
    title.pack(side=LEFT, fill='x', expand=True)

    # контейнер для текста (забирает оставшееся место)
    content_frame = Frame(theme_frame, bg='white')
    content_frame.pack(fill=BOTH, expand=True)

    # текст теории
    text_widget = Text(content_frame, wrap=WORD, font=('', 12), bg='white', state=DISABLED)
    scrollbar = Scrollbar(content_frame, orient=VERTICAL, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    text_widget.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0), pady=(0, 0))
    scrollbar.pack(side=RIGHT, fill=Y)

    # Загрузка теории
    theory_file_path = os.path.join(theme_folder_path, "theory.txt")
    try:
        with open(theory_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e: # <- ПРОВЕРКА НА ЗАГРУЗКУ ТЕОРИИ
        content = f"Ошибка загрузки теории:\n{str(e)}"

    text_widget.config(state=NORMAL)
    text_widget.delete(1.0, END)
    text_widget.insert(1.0, content)
    text_widget.config(state=DISABLED)

    # панель с тестом
    test_panel = Frame(theme_frame, bg='#f0f0f0', height=50)
    test_panel.pack(side='bottom', fill='x', padx=10, pady=(0, 10))
    test_panel.pack_propagate(False)

    total, completed = 0, 0
    test_file_path = os.path.join(theme_folder_path, "test.json")
    if os.path.exists(test_file_path):
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            if isinstance(test_data, list):
                total = len(test_data)
                completed = sum(1 for q in test_data if q.get("completed") is True)
        except: # <- ИСКЛЮЧЕНИЕ НА БИТЫЙ JSON
            pass

    Label(test_panel, text=f"Тест по теме ({completed}/{total})", bg='#f0f0f0', font=('', 12, 'bold')).pack(side=LEFT, padx=10)
    Button(test_panel,
           text="Начать →",
           command=lambda: start_test(theme_frame, theme_folder_path, total),
           bg='#45a049',
           fg='white',
           font=('Arial', 12, 'bold'),
           bd=0,
           relief='flat',
           pady=5).pack(side='right', padx=10)

def start_test(theme_frame, theme_folder_path, q_count):
    # путь к тесту
    test_file_path = os.path.join(theme_folder_path, "test.json")

    # главный фрейм для теста
    test_frame = Frame(theme_frame, bg='white')
    test_frame.place(relwidth=1, relheight=1)

    title_frame = Frame(test_frame, bg='#c8c8c8', height=60)
    title_frame.pack(fill='x', padx=15, pady=(0, 5))
    title_frame.pack_propagate(False)

    back_button = Button(
        title_frame,
        text="← Назад к теории",
        command=lambda: test_frame.destroy(),
        font=('Arial', 12, 'bold'),
        bg='#e0e0e0',
        fg='#222222',
        activebackground='#c0c0c0',
        activeforeground='#222222',
        bd=0,
        relief='flat'
    )
    back_button.pack(side=RIGHT, padx=(0, 15))

    # ЗАГОЛОВОК СВЕРХУ
    cur_q = [0]
    title = Label(
        title_frame,
        text=f"Вопрос {cur_q[0]+1}/{q_count}",
        bg='#c8c8c8',
        fg='#222222',
        font=('Arial', 24, 'bold'),
        anchor='w'
    )
    title.pack(side=LEFT, padx=(15, 0))

    # === ОТОБРАЖЕНИЕ ТЕКУЩЕГО ВОПРОСА ===
    cur_t_frame = None
    user_ans = []
    correct_ans = []

    def show_task(question_num):
        nonlocal user_ans, correct_ans
        user_ans.clear()
        correct_ans.clear()
        nonlocal cur_t_frame, test_frame, test_file_path

        if cur_t_frame:
            cur_t_frame.destroy()
        # создание фрейма для вопроса и ответов
        cur_t_frame = Frame(test_frame, bg='white')
        cur_t_frame.pack(fill='x', padx=15, pady=10)

        # чтение данных текущего теста
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                all_questions = json.load(f)

            if not isinstance(all_questions, list):
                raise Exception()

            if not (0 <= question_num < len(all_questions)):
                raise Exception()

            q = all_questions[question_num]

            if not all(field in q for field in ["question", "answers", "correct_answers"]):
                raise Exception()

            if not isinstance(q["answers"], list) or not isinstance(q["correct_answers"], list):
                raise Exception()

            answers_len = len(q["answers"])
            if any(not isinstance(i, int) or not (0 <= i < answers_len) for i in q["correct_answers"]):
                raise Exception()

            question = q["question"]
            answers = q["answers"]
            correct_ans = q["correct_answers"]

        except Exception: # <- ОБРАБОТКА ОТКРЫТИЯ JSONа
            messagebox.showerror("Ошибка", "Не удалось загрузить вопрос из файла теста.")
            test_frame.destroy()
            return

        # ФРЕЙМ ВОПРОСА
        quest_frame = LabelFrame(
            cur_t_frame,
            text="Задание",
            font=('Arial', 12, 'bold'),
            bg='#f9f9f9',
            padx=10,
            pady=5
        )
        quest_frame.pack(fill='x', pady=(0, 10))
        task_label = Label(
            quest_frame,
            text=question,
            bg='#f9f9f9',
            wraplength=1000,
            justify='left',
            anchor='w',
            font=('Arial', 12)
        )
        task_label.pack(fill='x')

        # ФРЕЙМ ДЛЯ ВАРИАНТОВ ОТВЕТОВ
        ans_frame = Frame(cur_t_frame, bg='white')
        ans_frame.pack(fill='x', pady=(0, 10))

        for ans_text in answers:
            var = BooleanVar()
            user_ans.append(var)
            row = Frame(ans_frame, bg='#f0f0f0')
            # Чекбокс слева
            cb = Checkbutton(row, variable=var, bg='#f0f0f0')
            cb.pack(side=LEFT, padx=(15, 10))
            # Текст ответа справа
            Label(
                row,
                text=ans_text,
                font=('Arial', 12),
                bg='#f0f0f0'
            ).pack(side=LEFT, anchor='w')
            row.pack(fill='x', pady=3)

        # ФРЕЙМ ДЛЯ ОТОБРАЖЕНИЯ ПРАВИЛЬНЫХ ОТВЕТОВ
        cor_ans_frame = Frame(cur_t_frame, bg='#f0f0f0')
        cor_ans_frame.pack(fill='x')

        cor_ans_visible = [False]
        # заполнение ответами
        c_ans_content_frame = Frame(cor_ans_frame, bg='#f0f0f0')

        for i in correct_ans:
            row = Frame(c_ans_content_frame, bg='#f0f0f0')
            Label(
                row,
                text=answers[i],
                font=('Arial', 12),
                bg='#f0f0f0'
            ).pack(anchor='w', padx=(35, 0), pady=2)
            row.pack(fill='x')

        def toggle_tests():
            if cor_ans_visible[0]:
                c_ans_content_frame.pack_forget()
                btn_toggle.config(text="Показать ответы")
            else:
                c_ans_content_frame.pack(fill='x', pady=5)
                btn_toggle.config(text="Скрыть ответы")
            cor_ans_visible[0] = not cor_ans_visible[0]

        btn_toggle = Button(
            cor_ans_frame,
            text="Показать ответы",
            command=toggle_tests,
            bg='#e0e0e0',
            fg='#222222',
            activebackground='#c0c0c0',
            activeforeground='#222222',
            font=('Arial', 12),
            bd=0,
            relief='flat',
            padx=10,
            pady=4
        )
        btn_toggle.pack(anchor='e', pady=(5, 0))

    # ===ФРЕЙМ ДЛЯ КНОПОК СНИЗУ===
    buttons_frame = Frame(test_frame, bg='white')
    buttons_frame.pack(fill='x', side='bottom', padx=15, pady=15)

    # фрейм для проверки ответов
    answer_frame = Frame(buttons_frame, bg='white')
    answer_frame.pack(fill='x', side='top', pady=(0, 10))
    check_button = Button(
        answer_frame,
        text="Проверить",
        command=lambda: check_answer(get_selected_indices(), correct_ans),
        font=('Arial', 12, 'bold'),
        bg='#e0e0e0',
        fg='#222222',
        activebackground='#c0c0c0',
        activeforeground='#222222',
        bd=0,
        relief='flat',
        padx=15,
        pady=5
    )
    check_button.pack(side=RIGHT)

    result = Label(answer_frame, bg='white', font=('Arial', 20, 'bold'))
    result.pack(side=LEFT)

    # фрейм для кнопок след. пред.
    swap_frame = Frame(buttons_frame, bg='white')
    swap_frame.pack(fill='x', side='bottom')
    next_btn = Button(
        swap_frame,
        text="Следующий вопрос ⟶",
        command=lambda: next_question(cur_q),
        font=('Arial', 12, 'bold'),
        bg='#e0e0e0',
        fg='#222222',
        activebackground='#c0c0c0',
        activeforeground='#222222',
        bd=0,
        relief='flat',
        padx=15,
        pady=5
    )
    next_btn.pack(side=RIGHT)

    prev_btn = Button(
        swap_frame,
        text="⟵ Предыдущий вопрос",
        command=lambda: latest_question(cur_q),
        font=('Arial', 12, 'bold'),
        bg='#e0e0e0',
        fg='#222222',
        activebackground='#c0c0c0',
        activeforeground='#222222',
        bd=0,
        relief='flat',
        padx=15,
        pady=5
    )
    prev_btn.pack(side=LEFT)

    def next_question(cur_q):
        nonlocal q_count, title, result
        if cur_q[0] + 1 == q_count:
            return

        cur_q[0] += 1
        title.config(text=f"Вопрос {cur_q[0] + 1}/{q_count}")
        result.config(text='', bg='white')
        show_task(cur_q[0])

    def latest_question(cur_q):
        nonlocal q_count, result
        if cur_q[0] == 0:
            return

        cur_q[0] -= 1
        title.config(text=f"Вопрос {cur_q[0] + 1}/{q_count}")
        result.config(text='', bg='white')
        show_task(cur_q[0])

    def get_selected_indices():
        return [i for i, var in enumerate(user_ans) if var.get()]

    def check_answer(user_ans, correct_ans):
        nonlocal cur_q, test_file_path
        if sorted(user_ans) == sorted(correct_ans):
            result.config(text="Правильно!", bg="lightgreen", fg="darkgreen")
            try:
                with open(test_file_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                test_data[cur_q[0]]["completed"] = True
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, ensure_ascii=False, indent=2)
            except Exception: # <- ОБРАБОТКА СОХРАНЕНИЯ В JSON
                messagebox.showwarning("Предупреждение", "Не удалось сохранить результат теста.")
        else:
            result.config(text="Ошибка!", bg="lightcoral", fg="darkred")

    # отображение первого вопроса
    show_task(cur_q[0])