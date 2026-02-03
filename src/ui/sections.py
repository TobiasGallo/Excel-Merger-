from tkinter import *
from tkinter import ttk

from src.config.constants import FONTS, FILE_LABELS
from .widgets import crear_boton


def build_header(parent, color_fn, on_tema_change):
    """Construye el header con titulo y toggle de tema.

    Returns:
        dict con widgets referenciables para aplicar_tema.
    """
    frame = Frame(parent, bg=color_fn("bg"))
    frame.pack(fill=X, pady=(0, 10))

    left = Frame(frame, bg=color_fn("bg"))
    left.pack(side=LEFT, fill=X, expand=True)

    title = Label(
        left, text="Excel Merger Pro+",
        font=FONTS["title"], fg=color_fn("primary"), bg=color_fn("bg"),
    )
    title.pack(anchor=W)

    subtitle = Label(
        left, text="Combina archivos Excel y CSV de forma sencilla y segura",
        font=FONTS["small"], fg=color_fn("text_sec"), bg=color_fn("bg"),
    )
    subtitle.pack(anchor=W)

    toggle = Frame(frame, bg=color_fn("bg"))
    toggle.pack(side=RIGHT, anchor=NE)

    btn_light = Button(
        toggle, text="Claro", font=FONTS["small"], width=6,
        cursor="hand2", relief="flat", bd=0,
        command=lambda: on_tema_change("light"),
    )
    btn_light.pack(side=LEFT, padx=2)

    btn_dark = Button(
        toggle, text="Oscuro", font=FONTS["small"], width=6,
        cursor="hand2", relief="flat", bd=0,
        command=lambda: on_tema_change("dark"),
    )
    btn_dark.pack(side=LEFT, padx=2)

    sep = Frame(parent, height=2, bg=color_fn("border"))
    sep.pack(fill=X, pady=(0, 15))

    return {
        "frame": frame, "left": left, "title": title, "subtitle": subtitle,
        "toggle": toggle, "btn_light": btn_light, "btn_dark": btn_dark, "sep": sep,
    }


def build_info(parent, color_fn):
    """Construye el panel de instrucciones."""
    frame = Frame(parent, bg=color_fn("info_bg"),
                  highlightbackground=color_fn("info_fg"), highlightthickness=1)
    frame.pack(fill=X, pady=(0, 15))

    title = Label(
        frame, text="  Instrucciones", font=FONTS["section"],
        bg=color_fn("info_bg"), fg=color_fn("info_fg"), anchor=W,
    )
    title.pack(fill=X, padx=12, pady=(10, 2))

    text = (
        "1.  Carga hasta 4 archivos (Excel o CSV). El Principal es la base del resultado.\n"
        "2.  Si un archivo tiene varias hojas, se te pedira seleccionar cual usar.\n"
        "3.  Configura las Claves de Combinacion: columnas que relacionan registros entre archivos.\n"
        "4.  Agrega columnas de los archivos secundarios al principal, o elimina columnas del principal.\n"
        "5.  Las claves pueden tener distintos nombres pero deben contener el mismo tipo de datos."
    )

    body = Label(
        frame, text=text, justify=LEFT, font=FONTS["small"],
        bg=color_fn("info_bg"), fg=color_fn("text_sec"), anchor=W,
    )
    body.pack(fill=X, padx=20, pady=(0, 10))

    return {"frame": frame, "title": title, "body": body}


def build_archivos(parent, color_fn, archivos, on_cargar, on_eliminar, on_hoja, on_agregar_slot):
    """Construye la seccion de carga de archivos.

    Args:
        archivos: Lista de 4 dicts con 'path' StringVar.
        on_cargar: Callback(indice).
        on_eliminar: Callback(indice).
        on_hoja: Callback(indice).
        on_agregar_slot: Callback().

    Returns:
        dict con widgets referenciables.
    """
    lf = ttk.LabelFrame(parent, text="  Archivos  ", padding=15)
    lf.pack(fill=X, pady=(0, 12))

    slots_frame = Frame(lf, bg=color_fn("surface"))
    slots_frame.pack(fill=X)

    widgets = []
    for i in range(4):
        slot = Frame(slots_frame, bg=color_fn("surface"))
        row = Frame(slot, bg=color_fn("surface"))
        row.pack(fill=X, pady=(0, 2))

        color = color_fn("file_colors")[i]

        btn_cargar = crear_boton(row, f"Cargar {FILE_LABELS[i]}",
                                 lambda idx=i: on_cargar(idx), color, width=22)
        btn_cargar.pack(side=LEFT)

        btn_x = Button(
            row, text="X", command=lambda idx=i: on_eliminar(idx),
            bg=color_fn("danger"), fg="white", font=("Segoe UI", 9, "bold"),
            width=3, relief="flat", cursor="hand2",
        )
        btn_x.pack(side=LEFT, padx=(8, 0))

        btn_hoja = Button(
            row, text="Hoja", command=lambda idx=i: on_hoja(idx),
            bg=color_fn("accent"), fg="white", font=("Segoe UI", 9, "bold"),
            width=5, relief="flat", cursor="hand2",
        )
        btn_hoja.pack(side=LEFT, padx=(8, 0))

        path_lbl = Label(
            slot, textvariable=archivos[i]["path"],
            fg=color, bg=color_fn("surface"), font=FONTS["small"], anchor=W,
        )
        path_lbl.pack(fill=X, pady=(0, 4))

        widgets.append({
            "slot": slot, "row": row, "btn_cargar": btn_cargar,
            "btn_eliminar": btn_x, "btn_hoja": btn_hoja, "path_lbl": path_lbl,
        })

    separadores = []
    for _ in range(3):
        sep = Frame(slots_frame, height=1, bg=color_fn("border"))
        separadores.append(sep)

    btn_frame = Frame(lf, bg=color_fn("surface"))
    btn_frame.pack(fill=X, pady=(8, 0))

    btn_agregar = crear_boton(btn_frame, "Agregar Archivo", on_agregar_slot,
                              color_fn("accent"), width=18)
    btn_agregar.pack()

    return {
        "lf": lf, "slots_frame": slots_frame, "widgets": widgets,
        "separadores": separadores, "btn_frame": btn_frame, "btn_agregar": btn_agregar,
    }


def build_claves(parent, color_fn):
    """Construye la seccion de claves de combinacion (sin filas, se agregan dinamicamente)."""
    lf = ttk.LabelFrame(parent, text="  Claves de Combinacion  ", padding=15)
    lf.pack(fill=X, pady=(0, 12))

    container = Frame(lf, bg=color_fn("surface"))
    container.pack(fill=X, pady=(0, 10))

    # El boton se agrega despues porque necesita el callback del App
    return {"lf": lf, "container": container, "btn_agregar": None}


def build_columnas_agregar(parent, color_fn):
    """Construye la seccion de columnas a agregar."""
    lf = ttk.LabelFrame(parent, text="  Columnas a Agregar  ", padding=15)
    lf.pack(fill=X, pady=(0, 12))

    container = Frame(lf, bg=color_fn("surface"))
    container.pack(fill=X, pady=(0, 10))

    return {"lf": lf, "container": container, "btn_agregar": None}


def build_columnas_eliminar(parent, color_fn):
    """Construye la seccion de columnas a eliminar."""
    lf = ttk.LabelFrame(parent, text="  Columnas a Eliminar del Principal  ", padding=15)
    lf.pack(fill=X, pady=(0, 12))

    container = Frame(lf, bg=color_fn("surface"))
    container.pack(fill=X, pady=(0, 10))

    return {"lf": lf, "container": container, "btn_agregar": None}


def build_botones(parent, color_fn, on_combinar, on_guardar):
    """Construye los botones principales."""
    sep = Frame(parent, height=2, bg=color_fn("border"))
    sep.pack(fill=X, pady=(5, 15))

    frame = Frame(parent, bg=color_fn("bg"))
    frame.pack(fill=X, pady=(0, 10))

    inner = Frame(frame, bg=color_fn("bg"))
    inner.pack()

    btn_combinar = crear_boton(inner, "Combinar Datos", on_combinar,
                               color_fn("primary"), width=24)
    btn_combinar.pack(side=LEFT, padx=12)

    btn_guardar = crear_boton(inner, "Guardar Resultado", on_guardar,
                              color_fn("secondary"), width=24)
    btn_guardar.pack(side=LEFT, padx=12)

    return {
        "sep": sep, "frame": frame, "inner": inner,
        "btn_combinar": btn_combinar, "btn_guardar": btn_guardar,
    }


def build_footer(parent, color_fn):
    """Construye el footer."""
    sep = Frame(parent, height=1, bg=color_fn("border"))
    sep.pack(fill=X, pady=(10, 5))

    label = Label(
        parent, text="Developed by Tobias Gallo  |  v.1.0.0",
        font=FONTS["small"], fg=color_fn("text_sec"), bg=color_fn("bg"),
    )
    label.pack(pady=(0, 15))

    return {"sep": sep, "label": label}
