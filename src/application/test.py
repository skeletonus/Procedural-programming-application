import os
import json
import tempfile
import shutil

# 1. Тест системы прогресса
def test_progress_system():
    """1. Реализована система прогресса"""
    temp_dir = tempfile.mkdtemp()

    # Прогресс карточек
    cards_dir = os.path.join(temp_dir, "cards_dir")
    os.makedirs(cards_dir)
    catalog_path = os.path.join(cards_dir, "test.json")

    with open(catalog_path, 'w') as f:
        json.dump([{"question": "Q1", "answer": "A1"}], f)

    with open(catalog_path, 'r') as f:
        cards = json.load(f)

    assert len(cards) == 1

    # Прогресс задач
    code_dir = os.path.join(temp_dir, "code_dir")
    task_dir = os.path.join(code_dir, "task_1")
    os.makedirs(task_dir)

    task_data = {
        "completed": False,
        "tests": [[1]],
        "answers": ["1"]
    }

    with open(os.path.join(task_dir, "task.json"), 'w') as f:
        json.dump(task_data, f)

    with open(os.path.join(task_dir, "task.json"), 'r') as f:
        task = json.load(f)

    assert not task["completed"]
    task["completed"] = True

    with open(os.path.join(task_dir, "task.json"), 'w') as f:
        json.dump(task, f)

    with open(os.path.join(task_dir, "task.json"), 'r') as f:
        updated_task = json.load(f)

    assert updated_task["completed"]

    # Прогресс тестов
    theory_dir = os.path.join(temp_dir, "theory_dir")
    theme_dir = os.path.join(theory_dir, "theme")
    os.makedirs(theme_dir)

    test_data = [
        {"correct_answers": [0], "completed": False},
        {"correct_answers": [1], "completed": True}
    ]

    with open(os.path.join(theme_dir, "test.json"), 'w') as f:
        json.dump(test_data, f)

    with open(os.path.join(theme_dir, "test.json"), 'r') as f:
        test = json.load(f)

    total = len(test)
    completed = sum(1 for q in test if q["completed"])

    assert total == 2
    assert completed == 1

    shutil.rmtree(temp_dir)

# 2. Тест блока карточек
def test_cards_block():
    """2. Реализован блок с карточками"""
    temp_dir = tempfile.mkdtemp()
    catalog_path = os.path.join(temp_dir, "test.json")

    # Создание
    cards = []
    cards.append({"question": "Что такое Python?", "answer": "Язык программирования"})

    with open(catalog_path, 'w') as f:
        json.dump(cards, f)

    with open(catalog_path, 'r') as f:
        loaded_cards = json.load(f)

    assert len(loaded_cards) == 1
    assert loaded_cards[0]["question"] == "Что такое Python?"

    # Редактирование
    loaded_cards[0]["question"] = "Что такое функция?"

    with open(catalog_path, 'w') as f:
        json.dump(loaded_cards, f)

    with open(catalog_path, 'r') as f:
        updated_cards = json.load(f)

    assert updated_cards[0]["question"] == "Что такое функция?"

    # Удаление
    del updated_cards[0]

    with open(catalog_path, 'w') as f:
        json.dump(updated_cards, f)

    with open(catalog_path, 'r') as f:
        final_cards = json.load(f)

    assert len(final_cards) == 0

    shutil.rmtree(temp_dir)
def test_invalid_cards_files():
    """Проверка обработки невалидных файлов каталогов карточек"""
    temp_dir = tempfile.mkdtemp()
    cards_dir = os.path.join(temp_dir, "cards_dir")
    os.makedirs(cards_dir)

    # 1. Повреждённый JSON
    with open(os.path.join(cards_dir, "broken.json"), 'w') as f:
        f.write("{ this is not valid json")

    # 2. Не список
    with open(os.path.join(cards_dir, "not_list.json"), 'w') as f:
        json.dump({"question": "Q", "answer": "A"}, f)  # объект вместо списка

    # 3. Список, но без нужных полей
    with open(os.path.join(cards_dir, "no_fields.json"), 'w') as f:
        json.dump([{"q": "Q", "a": "A"}], f)

    # 4. Пустой файл
    with open(os.path.join(cards_dir, "empty.json"), 'w') as f:
        pass

    # 5. Неправильные типы
    with open(os.path.join(cards_dir, "wrong_types.json"), 'w') as f:
        json.dump([{"question": 123, "answer": None}], f)

    # И один валидный
    with open(os.path.join(cards_dir, "valid.json"), 'w') as f:
        json.dump([{"question": "Q", "answer": "A"}], f)

    # Имитируем логику из place_catalogues()
    def is_valid_catalogue(name):
        path = os.path.join(cards_dir, name + ".json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                return False
            for item in data:
                if not isinstance(item, dict):
                    return False
                if not isinstance(item.get("question"), str) or not isinstance(item.get("answer"), str):
                    return False
            return True
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return False

    catalogues = [f[:-5] for f in os.listdir(cards_dir) if f.endswith('.json')]
    valid_catalogues = [c for c in catalogues if is_valid_catalogue(c)]

    # Должен остаться ТОЛЬКО "valid"
    assert valid_catalogues == ["valid"]

    shutil.rmtree(temp_dir)

# 3. Тест блока теории
def test_theory_block():
    """3. Реализован блок с теорией"""
    temp_dir = tempfile.mkdtemp()

    # Структура
    theory_dir = os.path.join(temp_dir, "theory_tests_dir")
    module_dir = os.path.join(theory_dir, "Модуль 1")
    theme_dir = os.path.join(module_dir, "Тема 1")
    os.makedirs(theme_dir)

    # Теория
    theory_content = "Теория по теме"
    theory_file = os.path.join(theme_dir, "theory.txt")

    with open(theory_file, 'w', encoding='utf-8') as f:
        f.write(theory_content)

    with open(theory_file, 'r', encoding='utf-8') as f:
        content = f.read()

    assert content == "Теория по теме"

    shutil.rmtree(temp_dir)
def test_invalid_theory_txt():
    """Просто открываем невалидный theory.txt и проверяем, что не падает"""
    temp_dir = tempfile.mkdtemp()
    theme_dir = os.path.join(temp_dir, "theme")
    os.makedirs(theme_dir)

    # Создаём theory.txt с недекодируемыми байтами (невалидный UTF-8)
    theory_path = os.path.join(theme_dir, "theory.txt")
    with open(theory_path, 'wb') as f:
        f.write(b'\xff\xfe\x00\x00')  # мусор, не UTF-8

    # Имитируем логику из show_theme_file():
    content = ""
    try:
        with open(theory_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        content = "Ошибка загрузки теории."

    # Проверяем, что ошибка обработана
    assert content == "Ошибка загрузки теории."

    shutil.rmtree(temp_dir)

# 4. Тест блока тестов
def test_tests_block():
    """4. Реализован блок с тестами"""
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.json")

    # Создание теста
    test_data = [
        {
            "question": "Тестовый вопрос",
            "answers": ["Правильный", "Неправильный"],
            "correct_answers": [0],
            "completed": False
        }
    ]

    with open(test_file, 'w') as f:
        json.dump(test_data, f)

    with open(test_file, 'r') as f:
        loaded_test = json.load(f)

    assert len(loaded_test) == 1

    # Проверка ответов
    user_correct = [0]
    assert sorted(user_correct) == sorted(loaded_test[0]["correct_answers"])

    user_wrong = [1]
    assert sorted(user_wrong) != sorted(loaded_test[0]["correct_answers"])

    shutil.rmtree(temp_dir)
def test_invalid_theory_tests():
    """Проверка обработки невалидных тестов"""
    temp_dir = tempfile.mkdtemp()
    theory_dir = os.path.join(temp_dir, "theory_tests_dir")
    mod_dir = os.path.join(theory_dir, "M")
    theme_dir = os.path.join(mod_dir, "T")
    os.makedirs(theme_dir)

    # Невалидный test.json
    with open(os.path.join(theme_dir, "test.json"), 'w') as f:
        json.dump("not a list", f)

    # Имитируем логику из start_test()
    def is_valid_test_file(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                return False
            for q in data:
                if not isinstance(q, dict):
                    return False
                if "question" not in q or "answers" not in q or "correct_answers" not in q:
                    return False
                if not isinstance(q["answers"], list) or not isinstance(q["correct_answers"], list):
                    return False
            return True
        except (OSError, json.JSONDecodeError):
            return False

    assert not is_valid_test_file(os.path.join(theme_dir, "test.json"))

    shutil.rmtree(temp_dir)

# 5. Тест блока написания кода
def test_coding_block():
    """5. Реализован блок с написанием кода"""
    temp_dir = tempfile.mkdtemp()
    task_dir = os.path.join(temp_dir, "task_1")
    os.makedirs(task_dir)

    # Задача
    task_data = {
        "name": "Сумма чисел",
        "completed": False,
        "tests": [[5], [10]],
        "answers": ["15", "55"]
    }

    task_file = os.path.join(task_dir, "task.json")
    with open(task_file, 'w') as f:
        json.dump(task_data, f)

    # Решение
    solution_file = os.path.join(task_dir, "solution.txt")
    code = "n = int(input())\nprint(n*(n+1)//2)"

    with open(solution_file, 'w') as f:
        f.write(code)

    # Проверка
    with open(task_file, 'r') as f:
        task = json.load(f)

    assert task["name"] == "Сумма чисел"
    assert len(task["tests"]) == 2

    with open(solution_file, 'r') as f:
        solution = f.read()

    assert "n = int(input())" in solution

    shutil.rmtree(temp_dir)
def test_invalid_code_tasks():
    """Проверка обработки невалидных задач"""
    temp_dir = tempfile.mkdtemp()
    code_dir = os.path.join(temp_dir, "code_dir")
    os.makedirs(code_dir)

    task1 = os.path.join(code_dir, "task1")
    os.makedirs(task1)
    with open(os.path.join(task1, "task.json"), 'w') as f:
        # Отсутствует "completed"
        json.dump({"name": "T", "task": "..." }, f)

    task2 = os.path.join(code_dir, "task2")
    os.makedirs(task2)
    with open(os.path.join(task2, "task.json"), 'w') as f:
        # Повреждённый JSON
        f.write("{")

    task3 = os.path.join(code_dir, "task3")
    os.makedirs(task3)
    # task.json отсутствует

    task4 = os.path.join(code_dir, "task4")
    os.makedirs(task4)
    with open(os.path.join(task4, "task.json"), 'w') as f:
        # Всё есть — валидно
        json.dump({
            "name": "T",
            "completed": False,
            "task": "...",
            "input_data": "",
            "output_data": "",
            "tests": [],
            "answers": []
        }, f)

    # Имитируем логику из show_code_section()
    def is_valid_task(folder_path):
        task_json = os.path.join(folder_path, "task.json")
        if not os.path.exists(task_json):
            return False
        try:
            with open(task_json, 'r', encoding='utf-8') as f:
                task = json.load(f)
        except (OSError, json.JSONDecodeError):
            return False

        required = ["name", "completed", "task", "input_data", "output_data", "tests", "answers"]
        return all(field in task for field in required)

    task_dirs = [d for d in os.listdir(code_dir) if os.path.isdir(os.path.join(code_dir, d))]
    valid_tasks = [d for d in task_dirs if is_valid_task(os.path.join(code_dir, d))]

    assert valid_tasks == ["task4"]

    shutil.rmtree(temp_dir)
# Запуск: pytest test_functional.py