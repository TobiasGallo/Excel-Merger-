
# Excel Merger Pro+

Herramienta de escritorio con interfaz grafica desarrollada en Python para combinar, enriquecer y depurar datos entre multiples archivos Excel y CSV mediante coincidencia de claves primarias.

---

## Descripcion General

**Excel Merger Pro+** permite integrar datos de hasta 4 archivos (Excel `.xlsx`/`.xls` o CSV) de forma visual e intuitiva. El usuario selecciona archivos, define claves de combinacion entre ellos, elige que columnas agregar o eliminar, y genera un archivo resultante combinado. Todo desde una interfaz grafica moderna con soporte para modo claro y oscuro.

## Problema que Resuelve

En muchos entornos de trabajo (administracion, contabilidad, logistica, RRHH) los datos estan dispersos en multiples planillas sin una clave unica compartida entre sistemas. Cruzar manualmente esa informacion en Excel es lento, tedioso y propenso a errores.

Excel Merger Pro+ automatiza ese proceso:

- Elimina el copiado manual entre archivos.
- Reduce errores humanos en el cruce de datos.
- Permite combinar multiples fuentes en un solo resultado limpio.
- Ahorra horas de trabajo repetitivo.

---

## Funcionalidades

### Carga y gestion de archivos
- Soporte para archivos **Excel** (`.xlsx`, `.xls`) y **CSV** (`.csv`).
- Carga de hasta **4 archivos** simultaneos (1 principal + 3 secundarios).
- **Seleccion de hoja**: si un archivo Excel tiene multiples hojas, se presenta un dialogo para elegir cual usar.
- **Cambio de hoja**: permite cambiar la hoja seleccionada en cualquier momento sin recargar el archivo.
- **Eliminacion individual** de archivos cargados con boton dedicado.
- Los slots de archivos 3 y 4 se agregan dinamicamente con el boton "Agregar Archivo".

### Claves de combinacion
- Sistema de **modelo estrella**: cada archivo secundario se cruza contra el principal.
- Hasta **3 filas de claves** simultaneas para cruces complejos.
- Cada fila muestra un combo por archivo cargado, permitiendo que las claves tengan **nombres distintos** en cada archivo.
- **Validacion de tipos**: detecta automaticamente si las columnas clave tienen tipos de datos compatibles (numerico vs texto) antes de combinar.
- **Normalizacion de texto**: elimina acentos, espacios extras y diferencias de mayusculas/minusculas para maximizar coincidencias.

### Columnas a agregar
- Seleccion de hasta **3 columnas** de archivos secundarios para incorporar al resultado.
- Cada fila permite elegir el archivo origen y la columna deseada.
- Los combos se actualizan dinamicamente al cargar/eliminar archivos.
- Los datos faltantes se rellenan con `"--"`.

### Columnas a eliminar
- Eliminacion de hasta **3 columnas** del archivo principal en el resultado final.
- Seleccion directa desde las columnas del archivo principal cargado.

### Interfaz grafica
- Desarrollada con **Tkinter** y **ttk** (tema "clam").
- **Modo claro y oscuro** con toggle en el header.
- Ventana inicial de **1100x800 px**, redimensionable con minimo de **900x600 px**.
- Scroll vertical para contenido extenso.
- Botones con estilo flat y codigo de colores por archivo.
- Mensajes de error, advertencia y exito contextuales.

### Logica de merge
- Merge secuencial: el principal se enriquece archivo por archivo.
- Tipo de join: **left join** (se conservan todos los registros del principal).
- Deteccion de **claves duplicadas** en archivos secundarios con advertencia al usuario.
- Las claves auxiliares del merge se eliminan automaticamente del resultado.

### Exportacion
- Guardado en formato **Excel** (`.xlsx` con motor `openpyxl`) o **CSV**.
- Dialogo de guardado con seleccion de formato.

---

## Estructura del Proyecto

```
Excel-merger/
├── main.py                      # Punto de entrada
├── hoja-de-excel.ico            # Icono de la aplicacion
├── README.md
│
└── src/
    ├── __init__.py
    ├── app.py                   # Clase principal ExcelMergerApp
    │
    ├── config/
    │   ├── __init__.py          # Re-exports de configuracion
    │   ├── themes.py            # Diccionarios THEME_LIGHT y THEME_DARK
    │   ├── constants.py         # Fuentes, etiquetas, limites, filetypes
    │   └── state.py             # Clase AppState (tema actual, color())
    │
    ├── core/
    │   ├── __init__.py          # Re-exports de logica
    │   ├── file_io.py           # Lectura/escritura de archivos, dialogo de hojas
    │   ├── merge.py             # Funcion mezclar_datos() con merge multi-archivo
    │   └── normalization.py     # Normalizacion de texto y validacion de tipos
    │
    └── ui/
        ├── __init__.py          # Re-exports de componentes UI
        ├── tooltip.py           # Clase Tooltip con soporte de temas
        ├── widgets.py           # Helper crear_boton()
        └── sections.py          # Funciones build_* para cada seccion de la UI
```

### Responsabilidad de cada modulo

| Modulo | Responsabilidad |
|--------|----------------|
| `main.py` | Configura `sys.path` (compatibilidad con PyInstaller) y lanza la app |
| `app.py` | Orquesta toda la aplicacion: ventana, scroll, UI, eventos, tema |
| `themes.py` | Define 18+ claves de color para cada tema (bg, surface, primary, etc.) |
| `constants.py` | Centraliza fuentes, etiquetas de archivos, limites y tipos de archivo |
| `state.py` | Mantiene el estado global del tema y expone `color(key)` |
| `file_io.py` | Lee columnas, DataFrames, guarda resultados, dialogo de seleccion de hoja |
| `merge.py` | Ejecuta el merge multi-archivo con validacion, normalizacion y limpieza |
| `normalization.py` | Normaliza texto (acentos, espacios, case) y detecta tipos de datos |
| `sections.py` | Construye cada seccion visual y retorna diccionarios de widgets |
| `widgets.py` | Factory de botones con estilo consistente |
| `tooltip.py` | Tooltip dinamico que respeta el tema activo |

---

## Casos de Uso

| Caso | Descripcion |
|------|-------------|
| **Facturacion** | Agregar datos de clientes (CUIT, direccion) a una planilla de facturas cruzando por nombre de empresa |
| **Inventario** | Unir codigos SKU con descripciones de producto y precios desde distintos proveedores |
| **RRHH** | Consolidar datos de empleados dispersos en multiples planillas (legajo, area, sueldo) |
| **Reportes** | Combinar informacion de ventas, stock y logistica en un unico reporte ejecutivo |
| **Soporte** | Enriquecer tickets con datos del cliente desde un CRM exportado a Excel |
| **Contabilidad** | Cruzar movimientos bancarios con registros internos para conciliacion |

---

## Ejemplo de Flujo de Trabajo

### 1. Archivos de entrada

**Archivo Principal (facturas.xlsx):**

| Cliente | Producto | Fecha |
|---------|----------|-------|
| Empresa A | Lapices | 2024-01-15 |
| Empresa B | Resmas | 2024-01-16 |
| Empresa C | Toner | 2024-01-17 |

**Archivo Secundario (clientes.xlsx):**

| Nombre | CUIT | Ciudad |
|--------|------|--------|
| Empresa A | 30-12345678-9 | Buenos Aires |
| Empresa B | 30-98765432-1 | Cordoba |

### 2. Configuracion en la app

- **Clave de combinacion**: `Cliente` (principal) = `Nombre` (secundario)
- **Columna a agregar**: `CUIT` desde Secundario
- **Columna a eliminar**: `Fecha` del Principal

### 3. Resultado

| Cliente | Producto | CUIT |
|---------|----------|------|
| Empresa A | Lapices | 30-12345678-9 |
| Empresa B | Resmas | 30-98765432-1 |
| Empresa C | Toner | -- |

> `Empresa C` no tenia coincidencia, por lo que CUIT queda como `"--"`. La columna `Fecha` fue eliminada segun la configuracion.

---

## Ventajas Competitivas

- **Multi-archivo**: combina hasta 4 fuentes simultaneamente, a diferencia de herramientas que solo permiten 2.
- **Claves flexibles**: las columnas clave pueden tener nombres distintos en cada archivo.
- **Normalizacion inteligente**: elimina acentos, espacios y diferencias de case automaticamente para maximizar coincidencias.
- **Validacion de tipos**: previene errores al detectar incompatibilidad de tipos antes del merge.
- **Formato dual**: trabaja tanto con Excel como con CSV, ideal para interoperabilidad.
- **Interfaz moderna**: modo claro/oscuro, ventana redimensionable, scroll automatico.
- **Sin dependencia de Office**: no requiere Microsoft Excel instalado.
- **Portable**: compatible con PyInstaller para distribuir como ejecutable.

---

## Herramientas y Tecnologias

| Herramienta | Uso |
|-------------|-----|
| **Python 3.7+** | Lenguaje base |
| **pandas** | Lectura, manipulacion y merge de DataFrames |
| **openpyxl** | Motor de escritura para archivos `.xlsx` |
| **tkinter / ttk** | Interfaz grafica nativa de Python |
| **unicodedata** | Normalizacion de texto Unicode (acentos, caracteres especiales) |
| **PyInstaller** | Empaquetado como ejecutable standalone (opcional) |

---

## Instalacion y Ejecucion

### Requisitos previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalacion de dependencias

```bash
pip install pandas openpyxl
```

> `tkinter` viene incluido con la instalacion estandar de Python en Windows. En Linux puede requerir: `sudo apt install python3-tk`

### Ejecucion

```bash
python main.py
```

### Generar ejecutable (opcional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=hoja-de-excel.ico --name="Excel Merger" main.py
```

El ejecutable se generara en la carpeta `dist/`.

---

## Arquitectura Tecnica

### Patron de diseno

La aplicacion sigue una arquitectura modular con separacion de responsabilidades:

- **Config**: configuracion pura (temas, constantes, estado) sin dependencias de UI.
- **Core**: logica de negocio (I/O, merge, normalizacion) independiente de la interfaz.
- **UI**: componentes visuales que reciben callbacks y funciones de color como parametros.
- **App**: orquestador que conecta UI con Core mediante eventos y callbacks.

### Flujo de datos

```
Usuario interactua con UI
        |
        v
App recibe evento (callback)
        |
        v
App invoca Core (file_io, merge)
        |
        v
Core procesa datos con pandas
        |
        v
App actualiza UI con resultado
```

### Sistema de temas

Los temas se implementan como diccionarios planos con 18+ claves de color. La clase `AppState` expone un metodo `color(key)` que retorna el valor hex del tema activo. Todos los componentes UI reciben `color_fn` como parametro, permitiendo tematizacion completa sin acoplar la UI a la implementacion del tema.

---

## Limitaciones Conocidas

- No soporta archivos protegidos con contrasena.
- No valida formatos especificos de campos (ej. formato CUIT, emails).
- Sin barra de progreso para archivos grandes.
- El rendimiento puede degradarse con archivos de mas de 50,000 filas.
- Maximo 3 claves de combinacion, 3 columnas a agregar y 3 a eliminar por operacion.
- No soporta merge de tipo inner, right ni outer (solo left join).

---

## Desarrollador

**Tobias Gallo**
tobiasgallo89@gmail.com

---

> Version: v1.0.0
