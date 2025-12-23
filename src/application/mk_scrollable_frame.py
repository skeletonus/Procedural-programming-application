from tkinter import *

canvas = None

def mkscframe(main_frame, f_bg='white', c_bg='white'):
    global canvas
    canvas = Canvas(main_frame, bg=c_bg, highlightthickness=0)
    scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=f_bg)

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.configure(yscrollcommand=scrollbar.set)

    def on_frame_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", on_frame_configure)

    canvas.bind("<MouseWheel>", _on_mousewheel)

    return scrollable_frame, scrollbar, canvas

def _on_mousewheel(event):
    global canvas
    scroll_units = -int(event.delta / 120)
    top, bottom = canvas.yview()

    if scroll_units < 0 and top <= 0.0:  # прокрутка вверх и уже наверху
        return
    if scroll_units > 0 and bottom >= 1.0:  # прокрутка вниз и уже внизу
        return

    canvas.yview_scroll(scroll_units, "units")

def bind_wheel_to_all(widget):
    widget.bind("<MouseWheel>", _on_mousewheel)
    for child in widget.winfo_children():
        bind_wheel_to_all(child)

def bind_all_children(scrollable_frame, scrollbar, canvas):
    bind_wheel_to_all(scrollable_frame)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)