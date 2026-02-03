import pandas as pd
from pandas import ExcelWriter
from tkinter import Toplevel, Label, Listbox, Frame, Button, SINGLE, END, BOTH, CENTER

from src.config.constants import FONTS


def leer_columnas(filepath, sheet=None):
    if filepath.lower().endswith(".csv"):
        df = pd.read_csv(filepath, nrows=0)
    else:
        df = pd.read_excel(filepath, sheet_name=sheet, nrows=0)
    return list(df.columns)


def leer_dataframe(filepath, sheet=None):
    if filepath.lower().endswith(".csv"):
        return pd.read_csv(filepath)
    else:
        return pd.read_excel(filepath, sheet_name=sheet)


def guardar_dataframe(df, filepath):
    if filepath.lower().endswith(".csv"):
        df.to_csv(filepath, index=False)
    else:
        with ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)


def seleccionar_hoja_dialog(filepath, parent, color_fn):
    """Muestra un dialogo para elegir la hoja de un archivo Excel.

    Args:
        filepath: Ruta al archivo Excel.
        parent: Ventana padre de tkinter.
        color_fn: Funcion que recibe una clave de color y retorna el valor hex.

    Returns:
        Nombre de la hoja seleccionada, o None si se cancelo.
    """
    try:
        xls = pd.ExcelFile(filepath)
        hojas = xls.sheet_names
        if len(hojas) <= 1:
            return hojas[0] if hojas else None

        resultado = {"hoja": None}
        dialog = Toplevel(parent)
        dialog.title("Seleccionar hoja")
        dialog.geometry("350x300")
        dialog.resizable(False, False)
        dialog.configure(bg=color_fn("surface"))
        dialog.transient(parent)
        dialog.grab_set()

        Label(
            dialog, text="El archivo tiene varias hojas.\nSelecciona una:",
            font=FONTS["body"], bg=color_fn("surface"), fg=color_fn("text"),
            justify=CENTER,
        ).pack(pady=(15, 10))

        listbox_frame = Frame(dialog, bg=color_fn("surface"))
        listbox_frame.pack(fill=BOTH, expand=True, padx=20)

        listbox = Listbox(
            listbox_frame, font=FONTS["body"], selectmode=SINGLE,
            bg=color_fn("bg"), fg=color_fn("text"),
            selectbackground=color_fn("primary"), selectforeground="white",
            relief="flat", highlightthickness=1, highlightcolor=color_fn("border"),
        )
        listbox.pack(fill=BOTH, expand=True)

        for h in hojas:
            listbox.insert(END, h)
        listbox.selection_set(0)

        def confirmar():
            sel = listbox.curselection()
            if sel:
                resultado["hoja"] = hojas[sel[0]]
            dialog.destroy()

        btn = Button(
            dialog, text="Aceptar", command=confirmar,
            bg=color_fn("primary"), fg="white", activebackground=color_fn("primary"),
            activeforeground="white", font=FONTS["button"], width=12,
            cursor="hand2", relief="flat", bd=0, padx=12, pady=6,
        )
        btn.pack(pady=10)

        dialog.wait_window()
        return resultado["hoja"]

    except Exception:
        return None
