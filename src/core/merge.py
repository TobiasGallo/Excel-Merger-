import pandas as pd
from tkinter import messagebox

from src.config.constants import FILE_LABELS
from .normalization import normalizar_texto, validar_tipos_datos
from .file_io import leer_dataframe


def mezclar_datos(archivos, key_rows, add_columns, del_columns):
    """Ejecuta el merge multi-archivo.

    Args:
        archivos: Lista de dicts con path, sheet, columns por archivo.
        key_rows: Lista de dicts con frame y combos de claves.
        add_columns: Lista de dicts con combo_archivo y combo_columna.
        del_columns: Lista de dicts con combo_columna.

    Returns:
        DataFrame resultado, o None si hubo error.
    """
    if not archivos[0]["path"].get():
        raise ValueError("Debes cargar el archivo Principal")

    sec_cargados = [i for i in range(1, 4) if archivos[i]["path"].get()]
    if not sec_cargados:
        raise ValueError("Debes cargar al menos un archivo secundario")

    if not key_rows:
        raise ValueError("Debe haber al menos una fila de claves")

    resultado = leer_dataframe(archivos[0]["path"].get(), archivos[0]["sheet"])

    for sec_idx in sec_cargados:
        df_sec = leer_dataframe(archivos[sec_idx]["path"].get(), archivos[sec_idx]["sheet"])

        claves_principal = []
        claves_sec = []
        for row in key_rows:
            combos = row["combos"]
            clave_pri = combos[0].get() if len(combos) > 0 else ""
            clave_sec = combos[sec_idx].get() if sec_idx < len(combos) else ""

            if clave_pri and clave_sec:
                claves_principal.append(clave_pri)
                claves_sec.append(clave_sec)

        if not claves_principal:
            continue

        if not validar_tipos_datos(resultado, df_sec, claves_principal, claves_sec):
            raise ValueError(
                f"Error de tipos entre Principal y {FILE_LABELS[sec_idx]}:\n"
                "Las columnas clave no tienen el mismo tipo de datos"
            )

        for c in claves_principal:
            resultado[c] = resultado[c].apply(normalizar_texto)
        for c in claves_sec:
            df_sec[c] = df_sec[c].apply(normalizar_texto)

        if df_sec.duplicated(subset=claves_sec).any():
            messagebox.showwarning(
                "Advertencia",
                f"El archivo {FILE_LABELS[sec_idx]} tiene claves duplicadas.\n"
                "Se conservara el ultimo registro.",
            )
            df_sec = df_sec.drop_duplicates(subset=claves_sec, keep='last')

        cols_agregar = []
        for col_row in add_columns:
            arch_sel = col_row["combo_archivo"].get()
            col_sel = col_row["combo_columna"].get()
            if arch_sel == FILE_LABELS[sec_idx] and col_sel:
                cols_agregar.append(col_sel)

        if cols_agregar:
            cols_traer = claves_sec + [c for c in cols_agregar if c not in claves_sec]
            merged = pd.merge(
                resultado, df_sec[cols_traer],
                left_on=claves_principal, right_on=claves_sec, how='left',
            )

            for c in claves_sec:
                if c not in claves_principal and c in merged.columns:
                    merged = merged.drop(columns=[c])

            for col in cols_agregar:
                if col in merged.columns:
                    merged[col] = merged[col].fillna("--")

            resultado = merged

    cols_eliminar = []
    for del_row in del_columns:
        col_sel = del_row["combo_columna"].get()
        if col_sel and col_sel in resultado.columns:
            cols_eliminar.append(col_sel)

    if cols_eliminar:
        resultado = resultado.drop(columns=cols_eliminar)

    return resultado
