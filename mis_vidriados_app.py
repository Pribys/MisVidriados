# Archivo: 04_mis_vidriados_app.py
# ------------------------------------------------------------
# Versión modificada del archivo principal para integrar
# el nuevo módulo Stull.
#
# Cambios realizados:
# - Importación de StullVista
# - Nuevo método _add_tab_stull()
# - Inclusión de la pestaña "Stull"
#
# No se altera ninguna lógica existente.
# ------------------------------------------------------------

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout

from teoria.teoria_vista import TeoriaVista
from vidriados.vidriados_vista import VidriadosVista
from materias_primas.materias_primas_vista import MateriasPrimasVista
from seger.seger_vista import SegerVista
from currie.currie_vista import CurrieVista
from cuaderno.cuaderno_vista import CuadernoVista

# NUEVO MÓDULO
from stull.stull_vista import StullVista


# -----------------------------------------------------------------------------
# Resolución de rutas portable
# -----------------------------------------------------------------------------

def get_base_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_user_data_path(subfolder: str = "") -> str:
    base_path = get_base_path()
    ruta = os.path.join(base_path, "datos_usuario")
    if subfolder:
        ruta = os.path.join(ruta, subfolder)
    return os.path.abspath(ruta)


def get_database_path() -> str:
    return get_user_data_path("vidriados.db")


# -----------------------------------------------------------------------------
# Ventana principal
# -----------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle("Mis Vidriados")
        self.resize(1000, 700)
        self._init_ui()

    def _init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._add_tab_teoria()
        self._add_tab_vidriados()
        self._add_tab_materias_primas()
        self._add_tab_seger()
        self._add_tab_currie()
        self._add_tab_stull()   # NUEVA PESTAÑA
        self._add_tab_cuaderno()

    def _add_tab_teoria(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(TeoriaVista("teoria/introduccion.html"))
        self.tabs.addTab(widget, "Teoría de vidriados")

    def _add_tab_vidriados(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.vidriados_vista = VidriadosVista(self.db_path)
        layout.addWidget(self.vidriados_vista)
        self.tabs.addTab(widget, "Vidriados")

    def _add_tab_materias_primas(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(MateriasPrimasVista(self.db_path))
        self.tabs.addTab(widget, "Materias primas")

    def _add_tab_seger(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(SegerVista(self.db_path, self.vidriados_vista))
        self.tabs.addTab(widget, "Cálculos Seger")

    def _add_tab_currie(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(CurrieVista(self.db_path))
        self.tabs.addTab(widget, "Método Ian Currie")

    def _add_tab_stull(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(StullVista(self.db_path))
        self.tabs.addTab(widget, "Stull")

    def _add_tab_cuaderno(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(CuadernoVista("cuaderno/notas"))
        self.tabs.addTab(widget, "Cuaderno")


# -----------------------------------------------------------------------------
# Arranque aplicación
# -----------------------------------------------------------------------------

def main():
    db_path = get_database_path()
    app = QApplication(sys.argv)
    window = MainWindow(db_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
