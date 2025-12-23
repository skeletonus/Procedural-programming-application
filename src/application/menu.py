from tkinter import *
from cards import show_cards_section
from coding import show_code_section
from theory import show_theory_section

current_frame = None
buttons = [show_cards_section, show_code_section, show_theory_section]
current_button = None

def place_menu(root, welcome_frame):
    global current_frame
    current_frame = welcome_frame

    frame_menu = Frame(root, bg='#d0d0d0')
    frame_menu.place(relx=0, rely=0, relwidth=0.15, relheight=1)

    button_style = {
        'bg': '#e0e0e0',
        'fg': '#222222',
        'activebackground': '#c0c0c0',
        'activeforeground': '#222222',
        'font': ('Arial', 13, 'bold'),
        'bd': 0,
        'relief': 'flat',
        'anchor': 'w',
        'padx': 15,
        'pady': 12,
    }

    spacing = {'pady': (18, 10)}

    b_cards = Button(frame_menu, text="Карточки", **button_style, command=lambda: change_frame(0,b_cards, root))
    b_cards.pack(fill='x', **spacing)

    b_code = Button(frame_menu, text="Написать код", **button_style, command=lambda: change_frame(1,b_code, root))
    b_code.pack(fill='x', **spacing)

    b_theory = Button(frame_menu, text="Теория и тесты", **button_style, command=lambda: change_frame(2,b_theory, root))
    b_theory.pack(fill='x', **spacing)

    btn_exit = Button(
        frame_menu,
        text="Выход",
        bg='#b0b0b0',
        fg='#333333',
        activebackground='#a0a0a0',
        activeforeground='#222222',
        font=('Arial', 12, 'bold'),
        bd=0,
        relief='flat',
        padx=15,
        pady=12,
        command=root.destroy
    )
    btn_exit.pack(side='bottom', fill='x', padx=15, pady=25)

def change_frame(section_index, button, root):
    global current_frame, buttons, current_button
    if current_frame:
        current_frame.destroy()

    if current_button:
        current_button.config(bg='#e0e0e0')
    current_button = button
    current_button.config(bg='#c0c0c0')

    current_frame = Frame(root, bg='white') # создание главного фрейма
    buttons[section_index](current_frame)