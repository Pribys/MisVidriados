# -*- coding: utf-8 -*-
"""
Archivo: cuaderno_vista_02.py

Versión modificada del módulo CuadernoVista.

Modificación realizada:
- Las notas ya no se guardan en la ruta recibida por parámetro.
- Ahora se gestionan exclusivamente desde:
      datos_usuario/cuaderno/notas
- Se crean automáticamente todas las carpetas necesarias (parents=True).
- No se altera ningún otro comportamiento del módulo.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabBar, QTextEdit, QTextBrowser, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path


class CuadernoVista(QWidget):
    """
    Cuaderno de notas en texto plano.

    - Pestañas compactas (solo el espacio necesario para el texto).
    - Una única zona de contenido.
    - Barra inferior con todas las acciones.
    - Cada pestaña corresponde a un archivo .txt.
    - Las notas se almacenan en datos_usuario/cuaderno/notas.
    """

    def __init__(self, ruta_notas: str):
        super().__init__()

        # ------------------------------------------------------------
        # MODIFICACIÓN:
        # Se fuerza la nueva ruta fija para versión ejecutable
        # ------------------------------------------------------------
        self.ruta_notas = Path("datos_usuario/cuaderno/notas")
        self.ruta_notas.mkdir(parents=True, exist_ok=True)
        # ------------------------------------------------------------

        self.archivos = []
        self._init_ui()
        self._cargar_notas_existentes()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        self.tabbar = QTabBar()
        self.tabbar.setExpanding(False)
        self.tabbar.setElideMode(Qt.ElideNone)
        self.tabbar.currentChanged.connect(self._cambiar_pestana)
        layout_principal.addWidget(self.tabbar)

        self.visor = QTextBrowser()
        self.editor = QTextEdit()

        fondo_gris = """
            QTextEdit, QTextBrowser {
                background-color: #f0f0f0;
            }
        """
        self.visor.setStyleSheet(fondo_gris)
        self.editor.setStyleSheet(fondo_gris)
        self.editor.setVisible(False)

        layout_principal.addWidget(self.visor)
        layout_principal.addWidget(self.editor)

        barra_botones = QHBoxLayout()

        self.btn_nueva = QPushButton("Nueva nota")
        self.btn_renombrar = QPushButton("Renombrar pestaña")
        self.btn_eliminar = QPushButton("Eliminar nota")
        self.btn_editar = QPushButton("Editar")
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setVisible(False)

        self.btn_nueva.clicked.connect(self._nueva_nota)
        self.btn_renombrar.clicked.connect(self._renombrar_pestana)
        self.btn_eliminar.clicked.connect(self._eliminar_nota)
        self.btn_editar.clicked.connect(self._activar_edicion)
        self.btn_guardar.clicked.connect(self._guardar_archivo)

        barra_botones.addWidget(self.btn_nueva)
        barra_botones.addWidget(self.btn_renombrar)
        barra_botones.addWidget(self.btn_eliminar)
        barra_botones.addStretch()
        barra_botones.addWidget(self.btn_editar)
        barra_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(barra_botones)

    def _cargar_notas_existentes(self):
        archivos = sorted(self.ruta_notas.glob("*.txt"))
        if not archivos:
            self._crear_nota("Notas", "nota_1.txt")
            return

        for archivo in archivos:
            self._anadir_pestana(archivo)

        self.tabbar.setCurrentIndex(0)
        self._cargar_archivo_actual()

    def _anadir_pestana(self, archivo: Path):
        nombre = archivo.stem.replace("_", " ").title()
        self.archivos.append(archivo)
        self.tabbar.addTab(nombre)

    def _crear_nota(self, nombre: str, nombre_archivo: str):
        archivo = self.ruta_notas / nombre_archivo
        if not archivo.exists():
            archivo.write_text("", encoding="utf-8")
        self._anadir_pestana(archivo)
        self.tabbar.setCurrentIndex(len(self.archivos) - 1)
        self._cargar_archivo_actual()

    def _nueva_nota(self):
        nombre, ok = QInputDialog.getText(self, "Nueva nota", "Nombre de la nota:")
        if not ok or not nombre.strip():
            return

        nombre_archivo = nombre.strip().lower().replace(" ", "_") + ".txt"
        self._crear_nota(nombre.strip(), nombre_archivo)

    def _renombrar_pestana(self):
        index = self.tabbar.currentIndex()
        if index < 0:
            return

        nombre_actual = self.tabbar.tabText(index)
        nombre, ok = QInputDialog.getText(
            self, "Renombrar pestaña", "Nuevo nombre:", text=nombre_actual
        )
        if not ok or not nombre.strip():
            return

        self.tabbar.setTabText(index, nombre.strip())

    def _eliminar_nota(self):
        index = self.tabbar.currentIndex()
        if index < 0:
            return

        nombre = self.tabbar.tabText(index)
        respuesta = QMessageBox.question(
            self,
            "Eliminar nota",
            f"¿Eliminar la nota '{nombre}'?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        archivo = self.archivos[index]
        if archivo.exists():
            archivo.unlink()

        self.archivos.pop(index)
        self.tabbar.removeTab(index)

        if self.archivos:
            self.tabbar.setCurrentIndex(0)
            self._cargar_archivo_actual()
        else:
            self.visor.setPlainText("")
            self.editor.setPlainText("")

    def _archivo_actual(self):
        index = self.tabbar.currentIndex()
        if index < 0 or index >= len(self.archivos):
            return None
        return self.archivos[index]

    def _cargar_archivo_actual(self):
        archivo = self._archivo_actual()
        if archivo is None or not archivo.exists():
            self.visor.setPlainText("")
            self.editor.setPlainText("")
            self._modo_lectura()
            return

        contenido = archivo.read_text(encoding="utf-8")
        self.visor.setPlainText(contenido)
        self.editor.setPlainText(contenido)
        self._modo_lectura()

    def _cambiar_pestana(self, index: int):
        self._cargar_archivo_actual()

    def _activar_edicion(self):
        self.editor.setVisible(True)
        self.visor.setVisible(False)
        self.btn_guardar.setVisible(True)
        self.btn_editar.setVisible(False)

    def _guardar_archivo(self):
        archivo = self._archivo_actual()
        if archivo is None:
            return

        contenido = self.editor.toPlainText()
        archivo.write_text(contenido, encoding="utf-8")
        self.visor.setPlainText(contenido)
        self._modo_lectura()

    def _modo_lectura(self):
        self.editor.setVisible(False)
        self.visor.setVisible(True)
        self.btn_guardar.setVisible(False)
        self.btn_editar.setVisible(True)
