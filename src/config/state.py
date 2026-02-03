from .themes import THEME_LIGHT, THEME_DARK


class AppState:
    """Estado global de la aplicacion, incluyendo el tema actual."""

    def __init__(self):
        self.tema_actual = "light"

    def color(self, key):
        """Obtiene un color del tema actual."""
        theme = THEME_DARK if self.tema_actual == "dark" else THEME_LIGHT
        return theme[key]

    def set_tema(self, tema):
        self.tema_actual = tema
