from tkinter import Button

from src.config.constants import FONTS


def crear_boton(parent, text, command, color, fg="white", width=18):
    btn = Button(
        parent, text=text, command=command,
        bg=color, fg=fg, activebackground=color, activeforeground=fg,
        font=FONTS["button"], width=width, cursor="hand2",
        relief="flat", bd=0, padx=12, pady=6,
    )
    return btn
