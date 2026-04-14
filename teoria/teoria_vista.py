
# Archivo: teoria_vista_01.py
# Modificación: Añadido botón "Margen" que inserta un bloque <div class="margen">
# con margen únicamente izquierdo mediante CSS.
# Cambio encapsulado sin alterar comportamiento previo.
import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabBar, QTextEdit, QTextBrowser
)
from PySide6.QtCore import QFile, QTextStream, QUrl
from pathlib import Path


class TeoriaVista(QWidget):
    """
    Vista del módulo Teoría de vidriados.
    Añade botón de margen izquierdo mediante clase CSS.
    """

    def __init__(self, archivo_introduccion: str, archivo_instrucciones: str = "teoria/instrucciones.html"):
        super().__init__()

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

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        self.tabbar = QTabBar()
        self.tabbar.setExpanding(False)
        layout_principal.addWidget(self.tabbar)

        for nombre, _ in self.archivos:
            self.tabbar.addTab(nombre)

        self.visor = QTextBrowser()
        self.editor = QTextEdit()

        fondo_gris = """
            QTextEdit, QTextBrowser {
                background-color: #f0f0f0;
            }
        """
        self.visor.setStyleSheet(fondo_gris + "\n p { margin: 0 0 0.4em 0; }")
        self.editor.setStyleSheet(fondo_gris)
        self.editor.setVisible(False)

        layout_principal.addWidget(self.visor)
        layout_principal.addWidget(self.editor)

        self._aplicar_tamano_fuente()

        barra = QHBoxLayout()

        self.btn_editar = QPushButton("Editar")
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setVisible(False)

        self.botonera_html = QHBoxLayout()
        self._crear_boton_html("Negrita", "<strong>", "</strong>")
        self._crear_boton_html("Cursiva", "<em>", "</em>")
        self._crear_boton_html("Sub", "<sub>", "</sub>")
        self._crear_boton_html("Sup", "<sup>", "</sup>")
        self._crear_boton_html("H1", "<h1>", "</h1>")
        self._crear_boton_html("H2", "<h2>", "</h2>")
        self._crear_boton_html("Párrafo", "<p>", "</p>")
        self._crear_boton_lista("Lista", "ul")
        self._crear_boton_lista("Lista num.", "ol")
        self._crear_boton_margen("Margen")

        self.botonera_widget = QWidget()
        self.botonera_widget.setLayout(self.botonera_html)
        self.botonera_widget.setVisible(False)

        self.btn_editar.clicked.connect(self._activar_edicion)
        self.btn_guardar.clicked.connect(self._guardar_archivo)

        barra.addWidget(self.btn_editar)
        barra.addWidget(self.btn_guardar)
        barra.addWidget(self.botonera_widget)

        self.btn_fuente_menos = QPushButton('A-')
        self.btn_fuente_mas = QPushButton('A+')

        self.btn_fuente_menos.clicked.connect(lambda: self._cambiar_tamano_fuente(-1))
        self.btn_fuente_mas.clicked.connect(lambda: self._cambiar_tamano_fuente(1))

        barra.addStretch()
        barra.addWidget(self.btn_fuente_menos)
        barra.addWidget(self.btn_fuente_mas)

        layout_principal.addLayout(barra)

#    def _archivo_actual(self) -> Path:
#        index = self.tabbar.currentIndex()
#        return self.archivos[index][1]
    
    def _archivo_actual(self) -> Path:
        index = self.tabbar.currentIndex()
        relativa = self.archivos[index][1]

        if getattr(sys, "frozen", False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(".")

        return base / relativa

    def _cargar_archivo_actual(self):
        ruta = self._archivo_actual()
        archivo = QFile(str(ruta))

        if not archivo.exists():
            self.visor.setHtml("<h1>Documento vacío</h1>")
            self.editor.setPlainText("")
            self._modo_lectura()
            return

        archivo.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(archivo)
        contenido = stream.readAll()
        archivo.close()

        self.editor.setPlainText(contenido)
        self._mostrar_contenido(contenido)
        self._modo_lectura()

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

    def _crear_boton_html(self, texto: str, apertura: str, cierre: str):
        boton = QPushButton(texto)
        boton.clicked.connect(
            lambda _, a=apertura, c=cierre: self._envolver_seleccion(a, c)
        )
        self.botonera_html.addWidget(boton)

    def _envolver_seleccion(self, apertura: str, cierre: str):
        cursor = self.editor.textCursor()
        texto = cursor.selectedText()
        cursor.insertText(f"{apertura}{texto}{cierre}")

    def _crear_boton_lista(self, texto: str, tipo: str):
        boton = QPushButton(texto)
        boton.clicked.connect(lambda _, t=tipo: self._insertar_lista(t))
        self.botonera_html.addWidget(boton)

    def _insertar_lista(self, tipo: str):
        cursor = self.editor.textCursor()
        texto = cursor.selectedText()

        if texto:
            lineas = texto.split("\u2029")
        else:
            lineas = [""]

        items = "\n".join(f"<li>{l}</li>" for l in lineas if l.strip() or len(lineas) == 1)
        html = f"<{tipo}>\n{items}\n</{tipo}>"

        cursor.insertText(html)

    def _crear_boton_margen(self, texto: str):
        boton = QPushButton(texto)
        boton.clicked.connect(self._insertar_margen)
        self.botonera_html.addWidget(boton)

    def _insertar_margen(self):
        cursor = self.editor.textCursor()
        texto = cursor.selectedText()

        if texto:
            lineas = texto.split("\u2029")
            contenido = "\n".join(lineas)
        else:
            contenido = ""

        bloque = f'<div class="margen">\n{contenido}\n</div>'
        cursor.insertText(bloque)

    def _activar_edicion(self):
        self.visor.setVisible(False)
        self.editor.setVisible(True)
        self.btn_guardar.setVisible(True)
        self.botonera_widget.setVisible(True)
        self.btn_editar.setVisible(False)

    def _guardar_archivo(self):
        contenido = self.editor.toPlainText()
        ruta = self._archivo_actual()

        archivo = QFile(str(ruta))
        archivo.open(QFile.WriteOnly | QFile.Text)
        stream = QTextStream(archivo)
        stream << contenido
        archivo.close()

        self._mostrar_contenido(contenido)
        self._modo_lectura()

    def _modo_lectura(self):
        self.editor.setVisible(False)
        self.visor.setVisible(True)
        self.btn_guardar.setVisible(False)
        self.botonera_widget.setVisible(False)
        self.btn_editar.setVisible(True)

    def _aplicar_tamano_fuente(self):
        font = self.visor.font()
        font.setPointSize(self.tamano_fuente)
        self.visor.setFont(font)
        self.editor.setFont(font)

    def _cambiar_tamano_fuente(self, delta: int):
        nuevo = self.tamano_fuente + delta
        if 8 <= nuevo <= 20:
            self.tamano_fuente = nuevo
            self._aplicar_tamano_fuente()
