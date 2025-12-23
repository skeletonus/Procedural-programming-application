from menu import place_menu
from tkinter import *

root = Tk() # объект окна

h = root.winfo_screenheight() #  получаем размеры экрана пользователя
w = root.winfo_screenwidth()
root['bg'] = '#000000' # цвет заднего фона
root.title("Процедурное программирование") # название окна
root.wm_attributes('-alpha', 1) # прозрачность окна
root.geometry(f'{w}x{h}') # размер окна
root.resizable(width = True, height=True) # может ли пользователь изменять размер окна

welcome_frame = Frame(root, bg='white')
welcome_frame.place(relx=0.15, rely=0, relwidth=0.85, relheight=1)

welcome_text = (
    "Добро пожаловать в обучающий симулятор!\n\n"
    "Здесь вы можете эффективно изучать основы программирования с помощью разных форматов:\n\n"
    "Карточки — создавайте свои каталоги и карточки для запоминания ключевых понятий\n"
    "Написать код — пишите и тестируйте код по поставленным задачам\n"
    "Теория и тесты — изучайте структурированные материалы по темам курса и закрепляйте при помощи тестов\n\n"
)
welcome = Label(welcome_frame,text=welcome_text,bg='white', wraplength=1300, font=('', 20),justify='left', anchor='w')
welcome.pack(padx=30, pady=30)

place_menu(root, welcome_frame) # размещение меню

root.mainloop() # ЗАПУСК ПРОГРАММЫ
