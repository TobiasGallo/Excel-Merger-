import sys
import os

# Asegurar que el directorio raiz esta en el path para imports
if getattr(sys, 'frozen', False):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, os.path.dirname(__file__))

from src.app import ExcelMergerApp


def main():
    app = ExcelMergerApp()
    app.run()


if __name__ == "__main__":
    main()
