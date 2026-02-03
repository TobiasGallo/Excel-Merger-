from tkinter import Toplevel, Label

from src.config.constants import FONTS


class Tooltip:
    def __init__(self, widget, text, color_fn):
        self.widget = widget
        self.text = text
        self.color_fn = color_fn
        self.tooltip_window = None
        self.widget.bind("<Enter>", self._mostrar)
        self.widget.bind("<Leave>", self._ocultar)

    def _mostrar(self, event=None):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = Label(
            self.tooltip_window, text=self.text,
            background=self.color_fn("tooltip_bg"),
            foreground=self.color_fn("tooltip_fg"),
            font=FONTS["small"], relief="flat", padx=8, pady=5, wraplength=300,
        )
        label.pack()

    def _ocultar(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
