import unicodedata
import pandas as pd


def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower()


def detectar_tipo_real(serie):
    tipos = []
    for valor in serie.head(100):
        valor = normalizar_texto(valor)
        try:
            float(valor)
            tipos.append('numero' if '.' in valor else 'entero')
        except (ValueError, TypeError):
            tipos.append('string')
    return max(set(tipos), key=tipos.count) if tipos else 'string'


def validar_tipos_datos(df1, df2, claves1, claves2):
    for c1, c2 in zip(claves1, claves2):
        tipo1 = detectar_tipo_real(df1[c1])
        tipo2 = detectar_tipo_real(df2[c2])
        if tipo1 != tipo2:
            return False
    return True
