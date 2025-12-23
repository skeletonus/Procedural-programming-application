from tkinter import *
from tkinter import simpledialog, messagebox
import os
import json
from mk_scrollable_frame import mkscframe, bind_all_children

CARDS_DIR = os.path.join('..', '..', 'data','cards_dir')

main_cards_frame = None
frame_catalogues = None
current_catalogue_frame = None
current_catalogue_name = None
current_card_frame = None
cur_re_card_frame = None
cur_cr_card_frame = None
card_ind = 0

def show_cards_section(m_cards_frame): # выводит части окна
    global main_cards_frame
    main_cards_frame = m_cards_frame
    main_cards_frame.place(relx=0.15, rely=0, relwidth=0.85, relheight=1)
    place_catalogues()

def place_catalogues():
    global frame_catalogues, main_cards_frame
    frame_catalogues = Frame(main_cards_frame, bg='#d0d0d0')
    frame_catalogues.place(relx=0.82, rely=0, relwidth=0.18, relheight=1)
    title_catalogues = Label(frame_catalogues, text=f"Каталоги карт({len(os.listdir(CARDS_DIR))})", bg='#d0d0d0', font=('', 12))
    title_catalogues.pack()

    scrollable_frame, scrollbar, canvas = mkscframe(frame_catalogues, f_bg = '#d0d0d0', c_bg = '#d0d0d0')

    catalogues = [f[:-5] for f in os.listdir(CARDS_DIR) if f.endswith('.json')]
    button_style = {
        'bg': '#f0f0f0',
        'fg': '#222222',
        'activebackground': '#c0c0c0',
        'activeforeground': '#222222',
        'font': ('Arial', 10,),
        'bd': 0,
        'relief': 'flat',
        'anchor': 'w',
        'wraplength': 225,
        'padx':5,
        'pady':5
    }
    spacing = {'pady': 5}

    valid_catalogues = []

    for ctl_name in catalogues:
        path = os.path.join(CARDS_DIR, ctl_name + ".json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Проверка: должен быть списком
            if not isinstance(data, list):
                continue

            # Проверка: каждый элемент — словарь с "question" и "answer" (строки)
            valid = True
            for item in data:
                if not isinstance(item, dict):
                    valid = False
                    break
                if not isinstance(item.get("question"), str) or not isinstance(item.get("answer"), str):
                    valid = False
                    break

            if valid:
                valid_catalogues.append(ctl_name)

        except (OSError, json.JSONDecodeError): # <- ПРОВЕРКА НА ВАЛИДНЫЙ JSON-КАТАЛОГ
            # Файл не читается или битый JSON — пропускаем
            continue

    # Отображаем только валидные каталоги
    for ctl_name in valid_catalogues:
        catalogue = Button(scrollable_frame, text=ctl_name, **button_style,
                           command=lambda ctl=ctl_name: use_catalogue(ctl))
        catalogue.pack(fill='x', **spacing)

    btn_create_catalogue = Button(frame_catalogues, text="+ Создать новый каталог", **button_style,
                                  command=create_catalogue)
    btn_create_catalogue.pack(side='bottom', fill='x', pady=10)

    bind_all_children(scrollable_frame, scrollbar, canvas)

def use_catalogue(ctl_name):
    global current_catalogue_name, current_catalogue_frame, main_cards_frame, card_ind
    if current_catalogue_frame:
        current_catalogue_frame.destroy()
        current_catalogue_frame = None
        card_ind = 0

    current_catalogue_name = ctl_name
    current_catalogue_frame = Frame(main_cards_frame, bg='white')
    current_catalogue_frame.place(relx=0, rely=0, relwidth=0.82, relheight=1)

    buttons_container = Frame(current_catalogue_frame, bg='white')
    buttons_container.pack(side='bottom', fill='x', padx=15, pady=15)

    # Цвета
    card_button_bg = '#e8e8e8'      # обычные кнопки (для карточек)
    catalogue_button_bg = '#bfbfbf' # нижний ряд — чуть темнее
    text_color = '#222222'
    font_size = 10

    # Группы кнопок
    groups = [
        (["← Предыдущая карточка", "Следующая карточка →"], [lambda: latest_card(), lambda: next_card()], card_button_bg),
        (["Редактировать карточку", "- Удалить карточку"], [lambda: re_card(), lambda: delete_card()], card_button_bg),
        (["+ Создать новую карточку", "Переименовать каталог", "- Удалить каталог"], [lambda: create_card(), lambda: rename_catalogue(), lambda: delete_catalogue()], catalogue_button_bg)
    ]

    def latest_card():
        global card_ind, cur_re_card_frame, cur_cr_card_frame
        if card_ind == 0 or get_card_count() == 0 or cur_re_card_frame or cur_cr_card_frame:
            return

        card_ind -= 1
        place_card()

    def next_card():
        global card_ind, cur_re_card_frame, cur_cr_card_frame
        if card_ind + 1 == get_card_count() or get_card_count() == 0 or cur_re_card_frame or cur_cr_card_frame:
            return

        card_ind += 1
        place_card()

    def re_card():
        global current_catalogue_name, current_catalogue_frame, cur_re_card_frame, cur_cr_card_frame

        if cur_re_card_frame:
            cur_re_card_frame.destroy()
            cur_re_card_frame = None
        if cur_cr_card_frame:
            return

        cur_re_card_frame = Frame(current_catalogue_frame, bg='#f2f2f2')
        cur_re_card_frame.place(relx=0.5, rely=0.2, anchor='n', relwidth=0.6, relheight=0.5)

        title = Label(cur_re_card_frame, text="Редактирование карточки", bg='#f2f2f2', fg='#222222',
                      font=('Segoe UI', 16, 'bold'))
        title.pack(pady=(20, 15))

        main_content = Frame(cur_re_card_frame, bg='#f2f2f2')
        main_content.pack(fill='both', expand=True, padx=30, pady=(0, 60))

        Label(main_content, text="Вопрос:", bg='#f2f2f2', fg='#555555', font=('Segoe UI', 12, 'bold'), anchor='w').pack(
            anchor='w', pady=(0, 5))
        question_entry = Text(main_content, height=4, font=('Segoe UI', 12), wrap=WORD, relief='solid', bd=1, padx=8,
                              pady=5)
        question_entry.pack(fill='x', pady=(0, 15))

        Label(main_content, text="Ответ:", bg='#f2f2f2', fg='#555555', font=('Segoe UI', 12, 'bold'), anchor='w').pack(
            anchor='w', pady=(0, 5))
        answer_entry = Text(main_content, height=4, font=('Segoe UI', 12), wrap=WORD, relief='solid', bd=1, padx=8,
                            pady=5)
        answer_entry.pack(fill='x', pady=(0, 15))

        # Загрузка данных
        try:
            path = os.path.join(CARDS_DIR, current_catalogue_name + ".json")
            with open(path, 'r', encoding='utf-8') as f:
                cards = json.load(f)
            current_card = cards[card_ind]
            question_entry.insert("1.0", current_card["question"])
            answer_entry.insert("1.0", current_card["answer"])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить карточку:\n{e}")
            cur_re_card_frame.destroy()
            return

        btn_frame = Frame(cur_re_card_frame, bg='#f2f2f2')
        btn_frame.place(relx=1.0, rely=1.0, x=-30, y=-20, anchor='se')

        cancel_btn = Button(btn_frame, text="Отмена", bg='#d0d0d0', fg='#222222', font=('Segoe UI', 10, 'bold'),
                            relief='flat', padx=12, pady=4,
                            command=lambda: ex())
        def ex():
            global cur_re_card_frame
            cur_re_card_frame.destroy()
            cur_re_card_frame = None
        cancel_btn.pack(side='right', padx=5)

        save_btn = Button(btn_frame, text="Сохранить", bg='#b0c4de', fg='#222222', font=('Segoe UI', 10, 'bold'),
                          relief='flat', padx=12, pady=4,
                          command=lambda: save_edited_card())

        save_btn.pack(side='right', padx=5)

        def save_edited_card():
            global current_card_frame, cur_re_card_frame
            if current_card_frame:
                current_card_frame.destroy()
                current_card_frame = None

            question = question_entry.get("1.0", "end-1c").strip()
            answer = answer_entry.get("1.0", "end-1c").strip()

            if not question or not answer:
                messagebox.showwarning("Ошибка", "Вопрос и ответ не могут быть пустыми.")
                return

            try:
                cards[card_ind]["question"] = question
                cards[card_ind]["answer"] = answer

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(cards, f, ensure_ascii=False, indent=4)

                messagebox.showinfo("Успех", "Карточка успешно сохранена!")
                cur_re_card_frame.destroy()
                cur_re_card_frame = None
                place_card()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить карточку:\n{e}")

    def delete_card():
        global cur_re_card_frame, cur_cr_card_frame
        if get_card_count() == 0 or cur_cr_card_frame:  # пустой каталог или создается карточка
            return

        global current_catalogue_name, current_card_frame, card_ind
        # Подтверждение
        confirmed = messagebox.askyesno("Подтверждение удаления", "Вы действительно хотите удалить эту карточку?")

        if not confirmed:
            return

        try:
            path = os.path.join(CARDS_DIR, current_catalogue_name + ".json")
            with open(path, 'r', encoding='utf-8') as f:  # загружаем старый каталог
                cards = json.load(f)

            del cards[card_ind]

            with open(path, 'w', encoding='utf-8') as f:  # записываем каталог без карточки
                json.dump(cards, f, ensure_ascii=False, indent=4)

            if current_card_frame:
                current_card_frame.destroy()  # Удаляем фрейм текущей карточки
                current_card_frame = None
            if cur_re_card_frame:
                cur_re_card_frame.destroy()
                cur_re_card_frame = None
            # отображение после удаления
            if len(cards) == 0:  # Каталог пуст — ничего не показываем
                messagebox.showinfo("Успех", "Карточка удалена. Каталог пуст.")

            else:
                if card_ind == len(cards):  # Корректируем индекс, если нужно
                    card_ind -= 1
                place_card()
                messagebox.showinfo("Успех", "Карточка удалена.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить карточку:\n{e}")

    def create_card():
        global current_catalogue_name, current_catalogue_frame, cur_re_card_frame, cur_cr_card_frame
        if cur_re_card_frame:
            return
        if cur_cr_card_frame:
            cur_cr_card_frame.destroy()
            cur_cr_card_frame = None

        cur_cr_card_frame = Frame(current_catalogue_frame, bg='#f2f2f2')
        cur_cr_card_frame.place(relx=0.5, rely=0.2, anchor='n', relwidth=0.6, relheight=0.5)

        title = Label(cur_cr_card_frame, text="Создание новой карточки", bg='#f2f2f2', fg='#222222',
                      font=('Segoe UI', 16, 'bold'))
        title.pack(pady=(20, 15))

        main_content = Frame(cur_cr_card_frame, bg='#f2f2f2')
        main_content.pack(fill='both', expand=True, padx=30, pady=(0, 60))

        Label(main_content, text="Вопрос:", bg='#f2f2f2', fg='#555555', font=('Segoe UI', 12, 'bold'), anchor='w').pack(
            anchor='w', pady=(0, 5))
        question_entry = Text(main_content, height=4, font=('Segoe UI', 12), wrap=WORD, relief='solid', bd=1, padx=8,
                              pady=5)
        question_entry.pack(fill='x', pady=(0, 15))

        Label(main_content, text="Ответ:", bg='#f2f2f2', fg='#555555', font=('Segoe UI', 12, 'bold'), anchor='w').pack(
            anchor='w', pady=(0, 5))
        answer_entry = Text(main_content, height=4, font=('Segoe UI', 12), wrap=WORD, relief='solid', bd=1, padx=8,
                            pady=5)
        answer_entry.pack(fill='x', pady=(0, 15))

        btn_frame = Frame(cur_cr_card_frame, bg='#f2f2f2')
        btn_frame.place(relx=1.0, rely=1.0, x=-30, y=-20, anchor='se')

        cancel_btn = Button(btn_frame, text="Отмена", bg='#d0d0d0', fg='#222222', font=('Segoe UI', 10, 'bold'),
                            relief='flat', padx=12, pady=4,
                            command=lambda: ex())
        def ex():
            global cur_cr_card_frame
            cur_cr_card_frame.destroy()
            cur_cr_card_frame = None
        cancel_btn.pack(side='right', padx=5)

        add_btn = Button(btn_frame, text="+ Добавить", bg='#b0c4de', fg='#222222', font=('Segoe UI', 10, 'bold'),
                         relief='flat', padx=12, pady=4,
                         command=lambda: save_new_card())

        add_btn.pack(side='right', padx=5)

        def save_new_card():
            global cur_cr_card_frame
            question = question_entry.get("1.0", "end-1c").strip()
            answer = answer_entry.get("1.0", "end-1c").strip()

            if not question or not answer:
                messagebox.showwarning("Ошибка", "Вопрос и ответ не могут быть пустыми.")
                return

            try:
                path = os.path.join(CARDS_DIR, current_catalogue_name + ".json")
                with open(path, 'r', encoding='utf-8') as f:
                    cards = json.load(f)

                cards.append({"question": question, "answer": answer})

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(cards, f, ensure_ascii=False, indent=4)

                messagebox.showinfo("Успех", "Карточка успешно добавлена!")
                cur_cr_card_frame.destroy()
                cur_cr_card_frame = None

                if get_card_count() == 1:
                    place_card()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить карточку:\n{e}")

    def rename_catalogue():
        global current_catalogue_name, frame_catalogues

        new_name = simpledialog.askstring("Переименовать каталог", "Введите новое имя каталога:",
                                          initialvalue=current_catalogue_name)  # Открываем диалог для ввода нового имени

        if not new_name: return  # пользователь отменил

        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning("Неверное имя", "Имя каталога не может быть пустым.")
            return

        # Пути к старому и новому файлам
        old_path = os.path.join(CARDS_DIR, current_catalogue_name + ".json")
        new_path = os.path.join(CARDS_DIR, new_name + ".json")

        # Проверка, не существует ли такой каталог
        if os.path.exists(new_path):
            messagebox.showwarning("Ошибка", f"Каталог с именем '{new_name}' уже существует.")
            return

        try:
            os.rename(old_path, new_path)

            current_catalogue_name = new_name  # Обновляем глобальную переменную

            frame_catalogues.destroy()  # Обновляем интерфейс
            place_catalogues()

            messagebox.showinfo("Успех", f"Каталог переименован в '{new_name}'.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переименовать каталог:\n{e}")

    def delete_catalogue():
        global current_catalogue_frame, current_catalogue_name, frame_catalogues

        # Подтверждение
        confirmed = messagebox.askyesno("Подтверждение удаления",
                                        f"Вы действительно хотите удалить каталог '{current_catalogue_name}'?\n""Все карточки в нём будут безвозвратно удалены!")

        if not confirmed:
            return

        try:
            path = os.path.join(CARDS_DIR, current_catalogue_name + ".json")
            if os.path.exists(path):
                os.remove(path)

            current_catalogue_frame.destroy()  # Удаляем фрейм текущего каталога
            current_catalogue_frame = None

            frame_catalogues.destroy()  # Обновляем список каталогов
            place_catalogues()

            messagebox.showinfo("Успех", f"Каталог '{current_catalogue_name}' удалён.")
            global current_card_frame, cur_re_card_frame, cur_cr_card_frame
            current_catalogue_name = None
            current_card_frame = None
            cur_re_card_frame = None
            cur_cr_card_frame = None

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить каталог:\n{e}")

    for texts, funcs, bg_color in groups:
        group_frame = Frame(buttons_container, bg='white')
        group_frame.pack(fill='x', pady=6)

        n = len(texts)
        for col in range(n):
            group_frame.grid_columnconfigure(col, weight=1, uniform="group")

        for i in range(n):
            btn = Button(
                group_frame,
                text=texts[i],
                bg=bg_color,
                fg=text_color,
                font=('Segoe UI', font_size, 'normal'),
                relief='flat',
                borderwidth=1,
                highlightthickness=0,
                padx=8,
                pady=6,
                command=lambda f=funcs[i]: f()
            )
            btn.grid(row=0, column=i, padx=4, sticky='ew')

    # загрузка фрейма первой карточки
    if get_card_count() != 0:
        place_card()

def place_card():
    global current_card_frame, card_ind
    if current_card_frame:
        current_card_frame.destroy()

    current_card_frame = Frame(current_catalogue_frame, bg='#f2f2f2')
    current_card_frame.place(relx=0.5, rely=0.2, anchor='n', relwidth=0.6, relheight=0.5)

    path = os.path.join(CARDS_DIR, current_catalogue_name + ".json")
    with open(path, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    top_content = Frame(current_card_frame, bg='#f2f2f2')
    top_content.pack(fill='both', expand=True, padx=30, pady=(20, 60))

    Label(
        top_content,
        text="Вопрос:",
        bg='#f2f2f2',
        fg='#555555',
        font=('Segoe UI', 12, 'bold'),
        anchor='w'
    ).pack(anchor='w', pady=(0, 5))

    Label(
        top_content,
        text=cards[card_ind]['question'],
        bg='#f2f2f2',
        fg='#222222',
        font=('Segoe UI', 13),
        wraplength=560,
        justify='left',
        anchor='w'
    ).pack(anchor='w', pady=(0, 30))

    answer_visible = [False]

    answer_label = Label(
        top_content,
        text="Ответ:",
        bg='#f2f2f2',
        fg='#555555',
        font=('Segoe UI', 12, 'bold'),
        anchor='w'
    )

    answer_text_label = Label(
        top_content,
        text=cards[card_ind]['answer'],
        bg='#f2f2f2',
        fg='#222222',
        font=('Segoe UI', 12),
        wraplength=560,
        justify='left',
        anchor='w'
    )

    btn_toggle = Button(
        current_card_frame,
        text="Показать ответ",
        bg='#d0d0d0',
        fg='#222222',
        font=('Segoe UI', 10),
        relief='flat',
        padx=10,
        pady=4
    )
    btn_toggle.place(relx=1.0, rely=1.0, x=-30, y=-20, anchor='se')

    def toggle_answer():
        if answer_visible[0]:
            answer_label.pack_forget()
            answer_text_label.pack_forget()
            btn_toggle.config(text="Показать ответ")
        else:
            answer_label.pack(anchor='w', pady=(0, 5))
            answer_text_label.pack(anchor='w')
            btn_toggle.config(text="Скрыть ответ")
        answer_visible[0] = not answer_visible[0]

    btn_toggle.config(command=toggle_answer)

def create_catalogue():
    name = simpledialog.askstring("Создать каталог", "Введите имя нового каталога:") # Открываем диалоговое окно для ввода имени каталога

    if name:  # Проверяем, что пользователь ввёл что-то (не нажал Cancel или не оставил пустым)
        name = name.strip()
        if not name:
            messagebox.showwarning("Неверное имя", "Имя каталога не может быть пустым.")
            return

        path = os.path.join(CARDS_DIR, name + ".json")
        if os.path.exists(path):
            messagebox.showwarning("Каталог уже существует", f"Каталог с именем '{name}' уже существует.")
        else:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", f"Каталог '{name}' успешно создан.")
                global frame_catalogues # обновление каталога
                frame_catalogues.destroy()
                place_catalogues()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать каталог:\n{e}")

def get_card_count():
    global current_catalogue_name
    path = os.path.join(CARDS_DIR, current_catalogue_name + ".json")
    if not os.path.exists(path):
        return 0
    try:
        with open(path, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        return len(cards)
    except:
        return 0