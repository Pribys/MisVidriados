"""
materias_primas_vista.py

Vista del módulo materias_primas.
Revisión 11:
- La columna "Finalidad" se interpreta como TEXTO PLANO
- Se elimina cualquier lógica JSON en este campo
- Se muestra solo el óxido (o óxidos) sin comillas ni corchetes
"""

import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QDialog
)
from PySide6.QtCore import Qt

from . import materias_primas_logica
from .materias_primas_dialogo import MateriasPrimasDialogo


_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _formatear_oxido(nombre: str) -> str:
    return nombre.translate(_SUBINDICES)


def _formatear_analisis(texto: str) -> str:
    try:
        datos = json.loads(texto)
    except Exception:
        return texto

    fila1_claves = ["SiO2", "Al2O3", "PPC"]
    fila1 = []
    fila2 = []

    for clave in fila1_claves:
        if clave in datos:
            fila1.append(f"{_formatear_oxido(clave)} {datos[clave]}")

    for clave, valor in datos.items():
        if clave not in fila1_claves:
            fila2.append(f"{_formatear_oxido(clave)} {valor}")

    return "   ".join(fila1) + "\n" + "   ".join(fila2)


def _formatear_finalidad(texto: str) -> str:
    """
    Finalidad como texto plano:
    - "CaO" -> CaO
    - "Na2O, K2O" -> Na₂O, K₂O
    """
    if not texto:
        return ""

    partes = [p.strip() for p in texto.split(",") if p.strip()]
    return ", ".join(_formatear_oxido(p) for p in partes)


class MateriasPrimasVista(QWidget):

    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self._init_ui()
        self._cargar_datos()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels([
            "Id",
            "Nombre",
            "Análisis químico",
            "Finalidad"
        ])

        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setWordWrap(True)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        self.tabla.setColumnWidth(3, 120)

        layout_principal.addWidget(self.tabla)

        layout_botones = QHBoxLayout()

        self.boton_nuevo = QPushButton("Nuevo")
        self.boton_editar = QPushButton("Editar")
        self.boton_borrar = QPushButton("Borrar")

        self.boton_nuevo.clicked.connect(self._nuevo)
        self.boton_editar.clicked.connect(self._editar)
        self.boton_borrar.clicked.connect(self._borrar)

        layout_botones.addWidget(self.boton_nuevo)
        layout_botones.addWidget(self.boton_editar)
        layout_botones.addWidget(self.boton_borrar)
        layout_botones.addStretch()

        layout_principal.addLayout(layout_botones)

    def _cargar_datos(self):
        datos = materias_primas_logica.listar(self.db_path)
        self.tabla.setRowCount(len(datos))

        for fila, materia in enumerate(datos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(materia["id"])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(materia["nombre"]))

            analisis_formateado = _formatear_analisis(materia["analisis_oxidos"])
            self.tabla.setItem(
                fila, 2,
                QTableWidgetItem(analisis_formateado)
            )

            finalidad_formateada = _formatear_finalidad(materia["finalidad"])
            self.tabla.setItem(
                fila, 3,
                QTableWidgetItem(finalidad_formateada)
            )

        self.tabla.resizeRowsToContents()

    def _id_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        return int(self.tabla.item(fila, 0).text())

    def _nuevo(self):
        dialogo = MateriasPrimasDialogo(parent=self)
        if dialogo.exec() == QDialog.Accepted:
            r = dialogo.resultado
            ok, error = materias_primas_logica.crear(
                self.db_path,
                nombre=r["nombre"],
                analisis_oxidos=r["analisis_oxidos"],
                finalidad=r["finalidad"]
            )
            if not ok:
                QMessageBox.critical(self, "Error", error)
                return
            self._cargar_datos()

    def _editar(self):
        id_materia = self._id_seleccionado()
        if id_materia is None:
            QMessageBox.warning(self, "Editar", "Seleccione una materia prima.")
            return

        materia = materias_primas_logica.obtener(self.db_path, id_materia)
        if not materia:
            QMessageBox.critical(self, "Error", "La materia prima no existe.")
            return

        dialogo = MateriasPrimasDialogo(
            nombre=materia["nombre"],
            finalidad=materia["finalidad"],
            analisis_oxidos=materia["analisis_oxidos"],
            parent=self
        )

        if dialogo.exec() == QDialog.Accepted:
            r = dialogo.resultado
            ok, error = materias_primas_logica.editar(
                self.db_path,
                id_materia=id_materia,
                nombre=r["nombre"],
                analisis_oxidos=r["analisis_oxidos"],
                finalidad=r["finalidad"]
            )
            if not ok:
                QMessageBox.critical(self, "Error", error)
                return
            self._cargar_datos()

    def _borrar(self):
        id_materia = self._id_seleccionado()
        if id_materia is None:
            QMessageBox.warning(self, "Borrar", "Seleccione una materia prima.")
            return

        confirmar = QMessageBox.question(
            self,
            "Borrar",
            "¿Está seguro de que desea borrar la materia prima seleccionada?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            ok, error = materias_primas_logica.eliminar(self.db_path, id_materia)
            if not ok:
                QMessageBox.critical(self, "Error", error)
                return
            self._cargar_datos()
