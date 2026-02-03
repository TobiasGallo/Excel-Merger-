import sys
import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import pandas as pd

from src.config.state import AppState
from src.config.constants import (
    FONTS, FILE_LABELS, MAX_FILES, MAX_KEY_ROWS, MAX_ADD_COLUMNS, MAX_DEL_COLUMNS,
    FILETYPES_LOAD, FILETYPES_SAVE,
)
from src.core.file_io import leer_columnas, leer_dataframe, guardar_dataframe, seleccionar_hoja_dialog
from src.core.merge import mezclar_datos
from src.ui.widgets import crear_boton
from src.ui.sections import (
    build_header, build_info, build_archivos, build_claves,
    build_columnas_agregar, build_columnas_eliminar, build_botones, build_footer,
)


class ExcelMergerApp:
    def __init__(self):
        self.state = AppState()
        self.C = self.state.color

        # Datos
        self.ventana = Tk()
        self.archivos = [{"path": StringVar(), "sheet": None, "columns": []} for _ in range(MAX_FILES)]
        self.key_rows = []
        self.add_columns = []
        self.del_columns = []
        self.df_final = None
        self.num_archivos_visibles = IntVar(value=2)

        self._setup_window()
        self._setup_styles()
        self._setup_scroll()
        self._build_ui()
        self._init_state()

    # ─── Setup ───────────────────────────────────────────────────────────────
    def _setup_window(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(__file__))

        self.ventana.title("Excel Merger Pro+")
        self.ventana.geometry("1100x800")
        self.ventana.resizable(True, True)
        self.ventana.minsize(900, 600)
        self.ventana.configure(bg=self.C("bg"))

        icon_path = os.path.join(base_path, "hoja-de-excel.ico")
        if os.path.exists(icon_path):
            self.ventana.wm_iconbitmap(icon_path)

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._apply_ttk_styles()

    def _apply_ttk_styles(self):
        self.style.configure("TCombobox", padding=4, font=FONTS["body"])
        self.style.configure("TScrollbar", background=self.C("border"))
        self.style.configure("TLabelframe", background=self.C("surface"),
                             borderwidth=1, relief="solid")
        self.style.configure("TLabelframe.Label", background=self.C("surface"),
                             font=FONTS["section"], foreground=self.C("text"))

    def _setup_scroll(self):
        self.main_frame = Frame(self.ventana, bg=self.C("bg"))
        self.main_frame.pack(fill=BOTH, expand=True)

        self.canvas = Canvas(self.main_frame, bg=self.C("bg"), highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical",
                                       command=self.canvas.yview)
        self.scrollable = Frame(self.canvas, bg=self.C("bg"))

        self.scrollable.bind("<Configure>",
                             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.content = Frame(self.scrollable, bg=self.C("bg"))
        self.content.pack(padx=40, pady=20, fill=BOTH, expand=True)

    # ─── Build UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.w_header = build_header(self.content, self.C, self._on_tema_change)
        self.w_info = build_info(self.content, self.C)
        self.w_archivos = build_archivos(
            self.content, self.C, self.archivos,
            self._cargar_archivo, self._eliminar_archivo,
            self._cambiar_hoja, self._agregar_slot_archivo,
        )
        self.w_claves = build_claves(self.content, self.C)
        self.w_claves["btn_agregar"] = crear_boton(
            self.w_claves["lf"], "Agregar Clave", self._agregar_fila_clave,
            self.C("accent"), fg="white", width=18,
        )
        self.w_claves["btn_agregar"].pack()

        self.w_add = build_columnas_agregar(self.content, self.C)
        self.w_add["btn_agregar"] = crear_boton(
            self.w_add["lf"], "Agregar Columna", self._agregar_columna_add,
            self.C("purple"), fg="white", width=18,
        )
        self.w_add["btn_agregar"].pack()

        self.w_del = build_columnas_eliminar(self.content, self.C)
        self.w_del["btn_agregar"] = crear_boton(
            self.w_del["lf"], "Eliminar Columna", self._agregar_columna_del,
            self.C("danger"), fg="white", width=18,
        )
        self.w_del["btn_agregar"].pack()

        self.w_botones = build_botones(self.content, self.C,
                                       self._on_combinar, self._on_guardar)
        self.w_footer = build_footer(self.content, self.C)

    def _init_state(self):
        self.aplicar_tema()
        self._actualizar_ui_archivos()

    # ─── Archivos ────────────────────────────────────────────────────────────
    def _cargar_archivo(self, indice):
        filename = filedialog.askopenfilename(filetypes=FILETYPES_LOAD)
        if not filename:
            return
        try:
            sheet = None
            if not filename.lower().endswith(".csv"):
                sheet = seleccionar_hoja_dialog(filename, self.ventana, self.C)
                if sheet is None:
                    xls = pd.ExcelFile(filename)
                    if len(xls.sheet_names) > 1:
                        return
                    sheet = xls.sheet_names[0]

            cols = leer_columnas(filename, sheet)
            self.archivos[indice]["path"].set(filename)
            self.archivos[indice]["sheet"] = sheet
            self.archivos[indice]["columns"] = cols
            self._actualizar_columnas()
            self._actualizar_ui_archivos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{str(e)}")

    def _eliminar_archivo(self, indice):
        self.archivos[indice]["path"].set("")
        self.archivos[indice]["sheet"] = None
        self.archivos[indice]["columns"] = []
        self._actualizar_columnas()
        self._actualizar_ui_archivos()

    def _cambiar_hoja(self, indice):
        filepath = self.archivos[indice]["path"].get()
        if not filepath:
            messagebox.showwarning("Aviso", "Primero carga un archivo")
            return
        if filepath.lower().endswith(".csv"):
            messagebox.showinfo("Info", "Los archivos CSV no tienen hojas")
            return
        try:
            xls = pd.ExcelFile(filepath)
            if len(xls.sheet_names) <= 1:
                messagebox.showinfo("Info", "Este archivo solo tiene una hoja")
                return
            nueva = seleccionar_hoja_dialog(filepath, self.ventana, self.C)
            if nueva and nueva != self.archivos[indice]["sheet"]:
                self.archivos[indice]["sheet"] = nueva
                self.archivos[indice]["columns"] = leer_columnas(filepath, nueva)
                self._actualizar_columnas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer las hojas:\n{str(e)}")

    def _agregar_slot_archivo(self):
        n = self.num_archivos_visibles.get()
        if n < MAX_FILES:
            self.num_archivos_visibles.set(n + 1)
            self._actualizar_ui_archivos()

    def _actualizar_ui_archivos(self):
        n = self.num_archivos_visibles.get()
        w = self.w_archivos

        for item in w["widgets"]:
            item["slot"].pack_forget()
        for s in w["separadores"]:
            s.pack_forget()

        for i in range(n):
            w["widgets"][i]["slot"].pack(fill=X, pady=2)
            if i < n - 1:
                w["separadores"][i].pack(fill=X, pady=4)

        if n >= MAX_FILES:
            w["btn_agregar"].pack_forget()
        else:
            w["btn_agregar"].pack()

        self._actualizar_claves_ui()

    # ─── Claves ──────────────────────────────────────────────────────────────
    def _agregar_fila_clave(self):
        if len(self.key_rows) >= MAX_KEY_ROWS:
            messagebox.showwarning("Limite", f"Maximo {MAX_KEY_ROWS} filas de claves")
            return

        container = self.w_claves["container"]
        frame = Frame(container, bg=self.C("surface"), pady=4)
        frame.pack(fill=X, pady=2)

        combos = []
        n = self.num_archivos_visibles.get()
        for i in range(n):
            color = self.C("file_colors")[i]
            Label(frame, text=f"{FILE_LABELS[i]}:", font=FONTS["body"],
                  bg=self.C("surface"), fg=color).pack(side=LEFT, padx=(0, 3))

            combo = ttk.Combobox(frame, width=15, state="readonly", font=FONTS["body"])
            combo.pack(side=LEFT, padx=(0, 12))

            if self.archivos[i]["path"].get():
                combo['values'] = self.archivos[i]["columns"]
            combos.append(combo)

        btn_x = Button(
            frame, text="X", command=lambda f=frame: self._eliminar_fila_clave(f),
            bg=self.C("danger"), fg="white", font=("Segoe UI", 9, "bold"),
            width=3, relief="flat", cursor="hand2",
        )
        btn_x.pack(side=LEFT, padx=5)

        self.key_rows.append({"frame": frame, "combos": combos})
        self._actualizar_columnas()

    def _eliminar_fila_clave(self, frame):
        self.key_rows = [r for r in self.key_rows if r["frame"] != frame]
        frame.destroy()

    def _actualizar_claves_ui(self):
        selecciones = [[c.get() for c in row["combos"]] for row in self.key_rows]
        for row in self.key_rows:
            row["frame"].destroy()
        self.key_rows.clear()

        for sel in selecciones:
            self._agregar_fila_clave()
            row = self.key_rows[-1]
            for j, combo in enumerate(row["combos"]):
                if j < len(sel) and sel[j]:
                    combo.set(sel[j])

    # ─── Columnas agregar ────────────────────────────────────────────────────
    def _agregar_columna_add(self):
        if len(self.add_columns) >= MAX_ADD_COLUMNS:
            messagebox.showwarning("Limite", f"Maximo {MAX_ADD_COLUMNS} columnas adicionales")
            return

        container = self.w_add["container"]
        frame = Frame(container, bg=self.C("surface"), pady=4)
        frame.pack(fill=X, pady=2)

        Label(frame, text="Archivo:", font=FONTS["body"],
              bg=self.C("surface"), fg=self.C("text_sec")).pack(side=LEFT, padx=(0, 3))

        combo_arch = ttk.Combobox(frame, width=14, state="readonly", font=FONTS["body"])
        combo_arch.pack(side=LEFT, padx=(0, 12))

        sec = [FILE_LABELS[i] for i in range(1, MAX_FILES) if self.archivos[i]["path"].get()]
        combo_arch['values'] = sec

        Label(frame, text="Columna:", font=FONTS["body"],
              bg=self.C("surface"), fg=self.C("text_sec")).pack(side=LEFT, padx=(0, 3))

        combo_col = ttk.Combobox(frame, width=18, state="readonly", font=FONTS["body"])
        combo_col.pack(side=LEFT, padx=(0, 10))

        def on_change(event):
            sel = combo_arch.get()
            for idx, lbl in enumerate(FILE_LABELS):
                if sel == lbl and self.archivos[idx]["path"].get():
                    combo_col['values'] = self.archivos[idx]["columns"]
                    combo_col.set("")
                    return
            combo_col['values'] = []
            combo_col.set("")

        combo_arch.bind("<<ComboboxSelected>>", on_change)

        btn_x = Button(
            frame, text="X", command=lambda f=frame: self._eliminar_columna_add(f),
            bg=self.C("danger"), fg="white", font=("Segoe UI", 9, "bold"),
            width=3, relief="flat", cursor="hand2",
        )
        btn_x.pack(side=LEFT, padx=5)

        self.add_columns.append({
            "frame": frame, "combo_archivo": combo_arch, "combo_columna": combo_col,
        })

    def _eliminar_columna_add(self, frame):
        self.add_columns = [c for c in self.add_columns if c["frame"] != frame]
        frame.destroy()

    # ─── Columnas eliminar ───────────────────────────────────────────────────
    def _agregar_columna_del(self):
        if len(self.del_columns) >= MAX_DEL_COLUMNS:
            messagebox.showwarning("Limite", f"Maximo {MAX_DEL_COLUMNS} columnas a eliminar")
            return

        container = self.w_del["container"]
        frame = Frame(container, bg=self.C("surface"), pady=4)
        frame.pack(fill=X, pady=2)

        Label(frame, text="Columna del Principal:", font=FONTS["body"],
              bg=self.C("surface"), fg=self.C("text_sec")).pack(side=LEFT, padx=(0, 3))

        combo = ttk.Combobox(frame, width=22, state="readonly", font=FONTS["body"])
        combo.pack(side=LEFT, padx=(0, 10))

        if self.archivos[0]["path"].get():
            combo['values'] = self.archivos[0]["columns"]

        btn_x = Button(
            frame, text="X", command=lambda f=frame: self._eliminar_columna_del(f),
            bg=self.C("danger"), fg="white", font=("Segoe UI", 9, "bold"),
            width=3, relief="flat", cursor="hand2",
        )
        btn_x.pack(side=LEFT, padx=5)

        self.del_columns.append({"frame": frame, "combo_columna": combo})

    def _eliminar_columna_del(self, frame):
        self.del_columns = [c for c in self.del_columns if c["frame"] != frame]
        frame.destroy()

    # ─── Actualizar combos ───────────────────────────────────────────────────
    def _actualizar_columnas(self):
        for row in self.key_rows:
            for i, combo in enumerate(row["combos"]):
                if i < len(self.archivos) and self.archivos[i]["path"].get():
                    combo['values'] = self.archivos[i]["columns"]
                else:
                    combo['values'] = []

        for col_row in self.add_columns:
            sel = col_row["combo_archivo"].get()
            if sel:
                for idx, lbl in enumerate(FILE_LABELS):
                    if sel == lbl and self.archivos[idx]["path"].get():
                        col_row["combo_columna"]['values'] = self.archivos[idx]["columns"]
                        break
                else:
                    col_row["combo_columna"]['values'] = []
            else:
                col_row["combo_columna"]['values'] = []

        for del_row in self.del_columns:
            if self.archivos[0]["path"].get():
                del_row["combo_columna"]['values'] = self.archivos[0]["columns"]
            else:
                del_row["combo_columna"]['values'] = []

    # ─── Acciones principales ────────────────────────────────────────────────
    def _on_combinar(self):
        try:
            self.df_final = mezclar_datos(
                self.archivos, self.key_rows, self.add_columns, self.del_columns,
            )
            messagebox.showinfo("Exito", "Datos combinados correctamente!\nDatos faltantes: '--'")
        except Exception as e:
            error_msg = str(e)
            if "tipos" in error_msg.lower():
                error_msg = "Error de tipos: Las columnas clave no tienen el mismo tipo de datos"
            messagebox.showerror("Error", error_msg)

    def _on_guardar(self):
        if self.df_final is None:
            messagebox.showerror("Error", "Primero debes combinar los datos")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=FILETYPES_SAVE,
            title="Guardar archivo combinado",
        )
        if filename:
            try:
                guardar_dataframe(self.df_final, filename)
                messagebox.showinfo("Exito", f"Archivo guardado en:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")

    # ─── Tema ────────────────────────────────────────────────────────────────
    def _on_tema_change(self, tema):
        self.state.set_tema(tema)
        self.aplicar_tema()

    def aplicar_tema(self):
        C = self.C
        self._apply_ttk_styles()

        self.ventana.configure(bg=C("bg"))
        self.main_frame.configure(bg=C("bg"))
        self.canvas.configure(bg=C("bg"))
        self.scrollable.configure(bg=C("bg"))
        self.content.configure(bg=C("bg"))

        # Header
        h = self.w_header
        for key in ("frame", "left", "toggle"):
            h[key].configure(bg=C("bg"))
        h["title"].configure(fg=C("primary"), bg=C("bg"))
        h["subtitle"].configure(fg=C("text_sec"), bg=C("bg"))
        h["sep"].configure(bg=C("border"))

        if self.state.tema_actual == "light":
            h["btn_light"].configure(bg=C("toggle_active"), fg="white")
            h["btn_dark"].configure(bg=C("toggle_inactive"), fg=C("text"))
        else:
            h["btn_light"].configure(bg=C("toggle_inactive"), fg=C("text"))
            h["btn_dark"].configure(bg=C("toggle_active"), fg="white")

        # Info
        info = self.w_info
        info["frame"].configure(bg=C("info_bg"), highlightbackground=C("info_fg"))
        info["title"].configure(bg=C("info_bg"), fg=C("info_fg"))
        info["body"].configure(bg=C("info_bg"), fg=C("text_sec"))

        # Archivos
        a = self.w_archivos
        a["slots_frame"].configure(bg=C("surface"))
        a["btn_frame"].configure(bg=C("surface"))
        a["btn_agregar"].configure(bg=C("accent"), fg="white", activebackground=C("accent"))

        for i, w in enumerate(a["widgets"]):
            color = C("file_colors")[i]
            w["slot"].configure(bg=C("surface"))
            w["row"].configure(bg=C("surface"))
            w["btn_cargar"].configure(bg=color, activebackground=color)
            w["btn_eliminar"].configure(bg=C("danger"), activebackground=C("danger"))
            w["btn_hoja"].configure(bg=C("accent"), fg="white", activebackground=C("accent"))
            w["path_lbl"].configure(fg=color, bg=C("surface"))

        for sep in a["separadores"]:
            sep.configure(bg=C("border"))

        # Claves
        self.w_claves["container"].configure(bg=C("surface"))
        if self.w_claves["btn_agregar"]:
            self.w_claves["btn_agregar"].configure(
                bg=C("accent"), fg="white", activebackground=C("accent"))

        for row in self.key_rows:
            row["frame"].configure(bg=C("surface"))
            for widget in row["frame"].winfo_children():
                if isinstance(widget, Label):
                    widget.configure(bg=C("surface"))

        # Columnas agregar
        self.w_add["container"].configure(bg=C("surface"))
        if self.w_add["btn_agregar"]:
            self.w_add["btn_agregar"].configure(
                bg=C("purple"), fg="white", activebackground=C("purple"))

        for col_row in self.add_columns:
            col_row["frame"].configure(bg=C("surface"))
            for widget in col_row["frame"].winfo_children():
                if isinstance(widget, Label):
                    widget.configure(bg=C("surface"), fg=C("text_sec"))

        # Columnas eliminar
        self.w_del["container"].configure(bg=C("surface"))
        if self.w_del["btn_agregar"]:
            self.w_del["btn_agregar"].configure(
                bg=C("danger"), fg="white", activebackground=C("danger"))

        for del_row in self.del_columns:
            del_row["frame"].configure(bg=C("surface"))
            for widget in del_row["frame"].winfo_children():
                if isinstance(widget, Label):
                    widget.configure(bg=C("surface"), fg=C("text_sec"))

        # Botones
        b = self.w_botones
        b["sep"].configure(bg=C("border"))
        b["frame"].configure(bg=C("bg"))
        b["inner"].configure(bg=C("bg"))
        b["btn_combinar"].configure(bg=C("primary"), activebackground=C("primary"))
        b["btn_guardar"].configure(bg=C("secondary"), activebackground=C("secondary"))

        # Footer
        f = self.w_footer
        f["sep"].configure(bg=C("border"))
        f["label"].configure(fg=C("text_sec"), bg=C("bg"))

    # ─── Run ─────────────────────────────────────────────────────────────────
    def run(self):
        self.ventana.mainloop()
