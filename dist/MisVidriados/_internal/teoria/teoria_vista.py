# Archivo: teoria_vista_03.py
# Versión corregida para ejecutable.
# Corrección: resolución robusta de rutas para HTML en desarrollo y PyInstaller.
# No altera otras funcionalidades del módulo.

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabBar, QTextBrowser
)
from PySide6.QtCore import QFile, QTextStream, QUrl
from pathlib import Path
import sys


class TeoriaVista(QWidget):
    """
    Vista pública del módulo Teoría de vidriados.
    Solo lectura. Sin edición.
    Resolución de rutas compatible con desarrollo y ejecutable.
    """

    def __init__(self, archivo_introduccion: str, archivo_instrucciones: str = "teoria/instrucciones.html"):
        super().__init__()

        self.base_path = self._get_base_path()

        self.archivos = [
            ("Instrucciones", Path("teoria/instrucciones.html")),
            ("Introducción", Path("teoria/introduccion.html")),
            ("Recetas", Path("teoria/recetas.html")),
            ("Fórmula Seger", Path("teoria/seger.html")),
            ("El vidrio", Path("teoria/vidrio.html")),
            ("Características", Path("teoria/caracteristicas.html")),
            ("Defectos", Path("teoria/defectos.html")),
            ("El color", Path("teoria/color.html")),
            ("Métodos", Path("teoria/metodos.html")),
        ]

        self.tamano_fuente = 11

        self._init_ui()
        self._cargar_archivo_actual()

        self.tabbar.currentChanged.connect(self._cambiar_pestana)

    def _get_base_path(self) -> Path:
        """
        Devuelve la ruta base real donde están los recursos.
        Compatible con:
        - Desarrollo
        - PyInstaller (--onedir y --onefile)
        """
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS)
        else:
            return Path(__file__).resolve().parent.parent

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        self.tabbar = QTabBar()
        self.tabbar.setExpanding(False)
        layout_principal.addWidget(self.tabbar)

        for nombre, _ in self.archivos:
            self.tabbar.addTab(nombre)

        self.visor = QTextBrowser()

        fondo_gris = """
            QTextBrowser {
                background-color: #f0f0f0;
            }
        """
        self.visor.setStyleSheet(fondo_gris + "\n p { margin: 0 0 0.4em 0; }")

        layout_principal.addWidget(self.visor)

        self._aplicar_tamano_fuente()

        barra = QHBoxLayout()

        self.btn_fuente_menos = QPushButton('A-')
        self.btn_fuente_mas = QPushButton('A+')

        self.btn_fuente_menos.clicked.connect(lambda: self._cambiar_tamano_fuente(-1))
        self.btn_fuente_mas.clicked.connect(lambda: self._cambiar_tamano_fuente(1))

        barra.addStretch()
        barra.addWidget(self.btn_fuente_menos)
        barra.addWidget(self.btn_fuente_mas)

        layout_principal.addLayout(barra)

    def _archivo_actual(self) -> Path:
        index = self.tabbar.currentIndex()
        relativa = self.archivos[index][1]
        return self.base_path / relativa

    def _cargar_archivo_actual(self):
        ruta = self._archivo_actual()
        archivo = QFile(str(ruta))

        if not archivo.exists():
            self.visor.setHtml("<h1>Documento vacío</h1>")
            return

        archivo.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(archivo)
        contenido = stream.readAll()
        archivo.close()

        self._mostrar_contenido(contenido)

    def _mostrar_contenido(self, contenido: str):
        texto = contenido.replace("\r\n", "\n")

        estilo = """
        <style>
        p { margin-bottom: 0.4em; }
        ul { list-style: none; margin-left: 1.2em; padding-left: 0; }
        ul li::before { content: '- '; }
        ol { list-style-type: decimal; margin-left: 1.2em; padding-left: 0; }
        li { margin: 0; padding: 0; }
        .margen { margin-left: 2em; }
        </style>
        """

        if "<p>" in texto or "<h1>" in texto or "<h2>" in texto:
            html = estilo + texto
        else:
            parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
            html = estilo
            html += "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in parrafos)

        base = QUrl.fromLocalFile(str(self._archivo_actual().parent.resolve()) + "/")
        self.visor.setHtml(html)
        self.visor.document().setBaseUrl(base)

    def _cambiar_pestana(self, index: int):
        self._cargar_archivo_actual()

    def _aplicar_tamano_fuente(self):
        font = self.visor.font()
        font.setPointSize(self.tamano_fuente)
        self.visor.setFont(font)

    def _cambiar_tamano_fuente(self, delta: int):
        nuevo = self.tamano_fuente + delta
        if 8 <= nuevo <= 20:
            self.tamano_fuente = nuevo
            self._aplicar_tamano_fuente()
