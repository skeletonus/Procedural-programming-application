import os
import json
from tkinter import *
from mk_scrollable_frame import mkscframe, bind_all_children
from tkinter import messagebox
import subprocess
import sys
import tempfile

CODE_DIR = os.path.join('..', '..', 'data', 'code_dir')

main_code_frame = None

def show_code_section(m_code_frame):
    global main_code_frame
    main_code_frame = m_code_frame
    main_code_frame.place(relx=0.15, rely=0, relwidth=0.85, relheight=1)

    scrollable_frame, scrollbar, canvas = mkscframe(main_code_frame, f_bg = 'white', c_bg =  'white')

    # Получаем список подпапок
    task_dirs = [d for d in os.listdir(CODE_DIR) if os.path.isdir(os.path.join(CODE_DIR, d))]

    for folder_name in task_dirs:
        folder_path = os.path.join(CODE_DIR, folder_name)
        task_json_path = os.path.join(folder_path, "task.json")

        try:
            with open(task_json_path, 'r', encoding='utf-8') as f:
                task = json.load(f)
        except (json.JSONDecodeError, IOError): #  <- ПРОВЕРКА НА БИТЫЕ ФАЙЛЫ
            continue  # пропускаем битые файлы

        name = task.get("name")
        themes = task.get("required_themes")
        completed = task.get("completed")

        # Формируем текст кнопки
        status = "{Выполнено} " if completed else "{Не выполнено} "
        themes_str = ", ".join(themes) if themes else "нет тем"
        button_text = f"{status}{name}\tТемы: {themes_str}"

        # Создаём кнопку
        btn = Button(scrollable_frame,
                     text=button_text,
                     bg='#e0e0e0',
                     fg='#222222',
                     activebackground='#c0c0c0',
                     activeforeground='#222222',
                     font=('Arial', 13),
                     anchor='w',
                     justify='left',
                     wraplength=1200,
                     bd=0,
                     relief='flat')
        btn.config(command=lambda fp=folder_path, b=btn: open_task(fp, b))
        btn.pack(fill='x', padx=15, pady=(8, 4))

    bind_all_children(scrollable_frame, scrollbar, canvas)

def open_task(folder_path, btn):
    global main_code_frame

    # Создаём новый фрейм поверх main_code_frame
    task_frame = Frame(main_code_frame, bg='#f0f0f0')
    task_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Заголовок
    header = Frame(task_frame, bg='#c8c8c8', height=50)
    header.pack(fill='x')
    header.pack_propagate(False)


    # Кнопка "Назад"
    btn_back = Button(header,
                         text="← Назад",
                         command=lambda: close_task_frame(task_frame, folder_path),
                         font=('Arial', 12, 'bold'),
                         bg='#e0e0e0',
                         fg='#222222',
                         activebackground='#c0c0c0',
                         activeforeground='#222222',
                         bd=0,
                         relief='flat')
    btn_back.pack(side='left', padx=10, pady=10)

    def close_task_frame(frame, folder_path):

        if not hasattr(frame, 'code_editor'): #  <- если не найден фрейм с кодом, то пропускаем сохранение
            frame.destroy()
            return
        code = frame.code_editor.get("1.0", "end-1c")
        # Проверяем, изменился ли код относительно файла
        solution_path = os.path.join(folder_path, "solution.txt")
        original_code = ""
        if os.path.exists(solution_path):
            try:
                with open(solution_path, 'r', encoding='utf-8') as f:
                    original_code = f.read()
            except (IOError, OSError, UnicodeDecodeError): # <- ПРОВЕРКА НА ЧТЕНИЕ КОДА
                # Если не прочитали — считаем, что "оригинал" пуст, и любые изменения = несохранённые
                original_code = ""

        if code.strip() != original_code.strip():
            res = messagebox.askyesnocancel("Сохранить?", "Код изменён. Сохранить перед выходом?")
            if res:
                save_code()
            elif res is None:
                return  # отмена

        frame.destroy()

    # Загружаем данные задачи
    task_json_path = os.path.join(folder_path, "task.json")
    try:
        with open(task_json_path, 'r', encoding='utf-8') as f:
            task = json.load(f)
    except (json.JSONDecodeError, IOError) as e: #  <- ПРОВЕРКА НА БИТЫЕ ФАЙЛЫ
        messagebox.showerror("Ошибка загрузки",
                             f"Не удалось загрузить задачу из папки:\n{folder_path}\n\nПодробности: {e}")
        task_frame.destroy()
        return

    # Проверка на наличие всех обязательных полей
    required_fields = ["name", "completed", "task", "input_data", "output_data", "tests", "answers"]
    missing_fields = [field for field in required_fields if field not in task]

    if missing_fields:
        error_msg = f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        messagebox.showerror(
            "Некорректная структура задачи",
            f"Файл задачи повреждён или неполный:\n{folder_path}\n\n{error_msg}"
        )
        task_frame.destroy()
        return

    name = task["name"]
    completed = task["completed"]
    task_text = task.get("task")
    input_example = task.get("input_data")
    output_example = task.get("output_data")
    tests = task.get("tests")
    answers = task.get("answers")

    # Название + статус
    status_icon = "{Выполнено} " if completed else "{Не выполнено} "
    title_label = Label(header, text=f"{name}   {status_icon}", font=('', 14, 'bold'), bg='#c8c8c8')
    title_label.pack(side='left')

    # Задание
    frame_task = LabelFrame(task_frame, text="Задание", font=('', 12, 'bold'), bg='#f9f9f9')
    frame_task.pack(fill='x', padx=10, pady=5)
    task_label = Label(frame_task, text=task_text, bg='#f9f9f9', wraplength=1000, justify='left', anchor='w')
    task_label.pack(fill='x', padx=10, pady=5)

    # Вход / Выход
    io_frame = Frame(task_frame, bg='#f0f0f0')
    io_frame.pack(fill='x', padx=10, pady=5)

    in_frame = LabelFrame(io_frame, text="Пример входных данных", font=('', 10), bg='#f9f9f9')
    in_frame.pack(side='left', fill='x', expand=True, padx=(0,10))
    Label(in_frame, text=input_example, bg='#f9f9f9', anchor='w').pack(fill='x', padx=5, pady=2)

    out_frame = LabelFrame(io_frame, text="Пример выходных данных", font=('', 10), bg='#f9f9f9')
    out_frame.pack(side='left', fill='x', expand=True)
    Label(out_frame, text=output_example, bg='#f9f9f9', anchor='w').pack(fill='x', padx=5, pady=2)

    # Тесты с кнопкой скрыть/показать
    tests_frame_container = Frame(task_frame, bg='#f0f0f0')
    tests_frame_container.pack(fill='x', padx=10, pady=5)

    tests_visible = [False]  # мутабельный флаг
    tests_content_frame = Frame(tests_frame_container, bg='#f0f0f0')

    def toggle_tests():
        if tests_visible[0]:
            tests_content_frame.pack_forget()
            btn_toggle.config(text="Показать тесты")
        else:
            tests_content_frame.pack(fill='x', pady=5)
            btn_toggle.config(text="Скрыть тесты")
        tests_visible[0] = not tests_visible[0]

    btn_toggle = Button(tests_frame_container,
                        text="Показать тесты",
                        command=toggle_tests,
                        bg='#e0e0e0',
                        fg='#222222',
                        activebackground='#c0c0c0',
                        activeforeground='#222222',
                        font=('Arial', 12),
                        bd=0,
                        relief='flat')
    btn_toggle.pack(anchor='e')

    # Заполняем тесты (но не показываем сразу)
    for i, (test, ans) in enumerate(zip(tests, answers)):
        row = Frame(tests_content_frame, bg='#f0f0f0')
        Label(row, text=f"Тест {i+1}: {test} → {ans}", font=('', 10), bg='#f0f0f0').pack(anchor='w')
        row.pack(fill='x')

    # Редактор кода
    code_label = Label(task_frame, text="Ваш код:", font=('', 12), bg='#f0f0f0')
    code_label.pack(anchor='w', padx=10, pady=(10,0))

    code_editor = Text(task_frame, font=('Consolas', 11), wrap='none', height=15)
    code_editor.pack(fill='both', expand=True, padx=10, pady=5)

    # Пытаемся загрузить сохранённый код
    solution_path = os.path.join(folder_path, "solution.txt")
    try:
        with open(solution_path, 'r', encoding='utf-8') as f:
            code_editor.insert('1.0', f.read())
    except (IOError, OSError, UnicodeDecodeError) as e: #  <- ПРОВЕРКА НА БИТЫЕ ФАЙЛЫ
        messagebox.showwarning(
            "Ошибка загрузки кода",
            f"Не удалось прочитать файл решения:\n{solution_path}\n\nОшибка: {e}"
        )

    # Кнопки внизу
    btn_frame = Frame(task_frame, bg='#f0f0f0')
    btn_frame.pack(fill='x', padx=10, pady=10)

    def run_code():
        code = code_editor.get("1.0", "end-1c").strip()
        if not code:
            messagebox.showwarning("Пустой код", "Напишите код перед запуском!")
            return

        # Создаём временный .py файл с кодом пользователя
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            user_code_path = f.name

        all_passed = True
        first_failure = None

        try:
            for i, (test_input, expected_output) in enumerate(zip(tests, answers)):
                # Формируем строку входных данных
                input_str = '\n'.join(map(str, test_input)) + ('\n' if test_input else '')

                try:
                    # Запускаем код в отдельном процессе
                    result = subprocess.run(
                        [sys.executable, user_code_path],
                        input=input_str,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5,  # максимум 5 секунд на тест <-ЗАЩИТА ОТ ЗАЦИКЛИВАНИЯ
                        cwd=os.path.dirname(user_code_path)
                    )

                    # Очищаем вывод от лишних пробелов и переносов
                    actual_output = result.stdout.strip()
                    expected_clean = expected_output.strip()

                    if actual_output == expected_clean:
                        continue
                    else:
                        all_passed = False
                        stderr_msg = result.stderr.strip()
                        first_failure = (i + 1, test_input, expected_clean, actual_output, stderr_msg)
                        break  # останавливаемся на первом проваленном тесте

                except subprocess.TimeoutExpired: # зацикливание <-ЗАЩИТА ОТ ЗАЦИКЛИВАНИЯ
                    all_passed = False
                    first_failure = (i + 1, test_input, expected_output.strip(), "[таймаут]", "")
                    break

                except Exception as e: # ошибки в коде
                    all_passed = False
                    first_failure = (i + 1, test_input, expected_output.strip(), f"[ошибка запуска]", str(e))
                    break

            # Вывод результата
            if all_passed:
                messagebox.showinfo("Успех!", "Все тесты пройдены!")
                # Обновляем completed = true в task.json
                task_path = os.path.join(folder_path, "task.json")
                with open(task_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                task_data["completed"] = True
                with open(task_path, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)

                # меняем статус на фреймах
                btn.config(text=btn["text"].replace("{Не выполнено} ", "{Выполнено} ", 1))
                title_label.config(text=title_label["text"].replace("{Не выполнено} ", "{Выполнено} ", 1))

            else:
                test_num, inp, exp, got, stderr = first_failure
                msg = f"Тест #{test_num} не пройден.\n\n"
                msg += f"Вход: {inp}\n"
                msg += f"Ожидалось: '{exp}'\n"
                msg += f"Получено:  '{got}'\n"
                if stderr:
                    msg += f"\nОшибки (stderr):\n{stderr[:600]}"
                messagebox.showerror("Ошибка", msg)

        finally:
            # Удаляем временный файл, даже если была ошибка
            try:
                os.unlink(user_code_path)
            except:
                pass

    def clear_code():
        code_editor.delete("1.0", "end")

    def save_code():
        code = code_editor.get("1.0", "end-1c")
        try:
            with open(solution_path, 'w', encoding='utf-8') as f:
                f.write(code)
            messagebox.showinfo("Сохранено", "Код успешно сохранён!")
        except (IOError, OSError) as e:
            messagebox.showerror(
                "Ошибка сохранения",
                f"Не удалось записать файл решения:\n{solution_path}\n\nОшибка: {e}"
            )

    Button(btn_frame,
              text="Запустить",
              command=run_code,
              bg='#45a049',
              fg='white',
              font=('Arial', 12, 'bold'),
              bd=0,
              relief='flat',
              pady=5).pack(side='left', padx=5)

    Button(btn_frame,
              text="Сохранить",
              command=save_code,
              bg='#1976d2',
              fg='white',
              font=('Arial', 12, 'bold'),
              bd=0,
              relief='flat',
              pady=5).pack(side='left', padx=5)

    Button(btn_frame,
              text="Очистить",
              command=clear_code,
              bg='#d32f2f',
              fg='white',
              font=('Arial', 12, 'bold'),
              bd=0,
              relief='flat',
              pady=5).pack(side='left', padx=5)

    # Сохраняем ссылки для save_current_task
    task_frame.code_editor = code_editor
    task_frame.solution_path = solution_path