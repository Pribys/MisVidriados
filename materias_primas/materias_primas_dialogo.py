"""
materias_primas_dialogo.py

Diálogo único para crear o editar una materia prima.

Revisión 04:
- Finalidad SE GUARDA SIEMPRE COMO TEXTO PLANO
- No se genera JSON en ningún caso para este campo
- Compatible con registros antiguos (JSON) al editar
"""

import json
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt


OXIDOS_DISPONIBLES = [
    "SiO2", "Al2O3", "Li2O", "Na2O", "K2O", "KNaO", "CaO", "MgO", "SrO", "BaO", 
    "Fe2O3", "TiO2", "ZnO", "B2O3", "P2O5", "PbO", "MnO", "ZrO2", "HfO2", "PPC"
]


def _finalidad_a_lista(texto: Optional[str]) -> List[str]:
    """
    Convierte finalidad antigua (JSON o texto) a lista limpia.
    """
    if not texto:
        return []
    texto = texto.strip()
    if texto.startswith("["):
        try:
            datos = json.loads(texto)
            if isinstance(datos, list):
                return [str(x) for x in datos]
        except Exception:
            pass
    return [p.strip() for p in texto.split(",") if p.strip()]


class MateriasPrimasDialogo(QDialog):

    def __init__(
        self,
        nombre: str = "",
        finalidad: Optional[str] = None,
        analisis_oxidos: Optional[str] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Materia prima")
        self.resize(600, 500)

        self._analisis: Dict[str, float] = {}
        self._finalidad: List[str] = _finalidad_a_lista(finalidad)

        if analisis_oxidos:
            try:
                self._analisis = json.loads(analisis_oxidos)
            except Exception:
                self._analisis = {}

        self._init_ui(nombre)

    def _init_ui(self, nombre: str):
        layout_principal = QVBoxLayout(self)

        grid = QGridLayout()

        grid.addWidget(QLabel("Nombre"), 0, 0)
        self.edit_nombre = QLineEdit(nombre)
        grid.addWidget(self.edit_nombre, 0, 1, 1, 2)

        grid.addWidget(QLabel("Finalidad (0–2 óxidos)"), 1, 0)

        self.combo_finalidad = QComboBox()
        self.combo_finalidad.addItem("— ninguna —", "")
        for ox in OXIDOS_DISPONIBLES:
            self.combo_finalidad.addItem(ox, ox)
        grid.addWidget(self.combo_finalidad, 1, 1)

        self.combo_finalidad_2 = QComboBox()
        self.combo_finalidad_2.addItem("— ninguna —", "")
        for ox in OXIDOS_DISPONIBLES:
            self.combo_finalidad_2.addItem(ox, ox)
        grid.addWidget(self.combo_finalidad_2, 1, 2)

        layout_principal.addLayout(grid)

        if len(self._finalidad) > 0:
            i = self.combo_finalidad.findData(self._finalidad[0])
            if i >= 0:
                self.combo_finalidad.setCurrentIndex(i)
        if len(self._finalidad) > 1:
            i = self.combo_finalidad_2.findData(self._finalidad[1])
            if i >= 0:
                self.combo_finalidad_2.setCurrentIndex(i)

        layout_principal.addWidget(QLabel("Análisis químico"))

        self.combo_oxidos = QComboBox()
        self._actualizar_combo_oxidos()
        self.combo_oxidos.currentIndexChanged.connect(self._oxido_seleccionado)
        layout_principal.addWidget(self.combo_oxidos)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Óxido", "% en peso", ""])
        self.tabla.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionMode(QAbstractItemView.NoSelection)
        layout_principal.addWidget(self.tabla)

        for oxido, valor in self._analisis.items():
            self._añadir_fila_analisis(oxido, valor)

        botones = QHBoxLayout()
        botones.addStretch()

        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")

        btn_guardar.clicked.connect(self._guardar)
        btn_cancelar.clicked.connect(self.reject)

        botones.addWidget(btn_guardar)
        botones.addWidget(btn_cancelar)

        layout_principal.addLayout(botones)

    def _actualizar_combo_oxidos(self):
        self.combo_oxidos.blockSignals(True)
        self.combo_oxidos.clear()
        self.combo_oxidos.addItem("Añadir óxido…", None)
        for ox in OXIDOS_DISPONIBLES:
            if ox not in self._analisis:
                self.combo_oxidos.addItem(ox, ox)
        self.combo_oxidos.blockSignals(False)

    def _oxido_seleccionado(self, index: int):
        oxido = self.combo_oxidos.itemData(index)
        if not oxido:
            return
        self._analisis[oxido] = 0.0
        self._añadir_fila_analisis(oxido, 0.0)
        self._actualizar_combo_oxidos()

    def _añadir_fila_analisis(self, oxido: str, valor: float):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)

        item_ox = QTableWidgetItem(oxido)
        item_ox.setFlags(Qt.ItemIsEnabled)
        self.tabla.setItem(fila, 0, item_ox)

        self.tabla.setItem(fila, 1, QTableWidgetItem(str(valor)))

        btn = QPushButton("✕")
        btn.clicked.connect(lambda _, f=fila: self._eliminar_fila(f))
        self.tabla.setCellWidget(fila, 2, btn)

    def _eliminar_fila(self, fila: int):
        oxido = self.tabla.item(fila, 0).text()
        self.tabla.removeRow(fila)
        self._analisis.pop(oxido, None)
        self._actualizar_combo_oxidos()

    def _guardar(self):
        nombre = self.edit_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Datos incompletos", "El nombre es obligatorio.")
            return

        analisis: Dict[str, float] = {}
        for fila in range(self.tabla.rowCount()):
            ox = self.tabla.item(fila, 0).text()
            try:
                val = float(self.tabla.item(fila, 1).text())
            except Exception:
                QMessageBox.warning(self, "Error", f"Valor incorrecto para {ox}.")
                return
            if val < 0:
                QMessageBox.warning(self, "Error", f"Valor negativo en {ox}.")
                return
            analisis[ox] = val

        if not analisis:
            QMessageBox.warning(self, "Error", "El análisis químico está vacío.")
            return

        finalidad = []
        if self.combo_finalidad.currentData():
            finalidad.append(self.combo_finalidad.currentData())
        if self.combo_finalidad_2.currentData() and self.combo_finalidad_2.currentData() not in finalidad:
            finalidad.append(self.combo_finalidad_2.currentData())

        # TEXTO PLANO, SIN JSON
        finalidad_texto = ", ".join(finalidad)

        self.resultado = {
            "nombre": nombre,
            "finalidad": finalidad_texto,
            "analisis_oxidos": json.dumps(analisis, ensure_ascii=False)
        }

        self.accept()
