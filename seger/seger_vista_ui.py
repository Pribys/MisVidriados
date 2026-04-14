
"""
Construcción de la interfaz gráfica del módulo Seger.

Versión 07:
- Añade campo de incremento '+-:' para modificar pesos
  en modo receta → fórmula.
- El campo se sitúa a la izquierda del campo Total.
- No contiene lógica de negocio.
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QListWidget, QLineEdit,
    QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QTableWidget, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView


def construir_ui(vista):
    layout_principal = QHBoxLayout(vista)

    col_izq = QVBoxLayout()
    col_izq.addWidget(QLabel("Materias primas"))
    vista.lista_materias = QListWidget()
    col_izq.addWidget(vista.lista_materias)
    cont_izq = QWidget()
    cont_izq.setLayout(col_izq)

    col_der = QVBoxLayout()

    receta_box = QGroupBox("Receta")
    receta_layout = QVBoxLayout(receta_box)

    vista.tabla_receta = QTableWidget()
    vista.tabla_receta.setColumnCount(6)
    vista.tabla_receta.setHorizontalHeaderLabels(
        ["MP", "Peso (g)", "+", "-", "%", "Cantidad"]
    )
    vista.tabla_receta.verticalHeader().setVisible(False)
    vista.tabla_receta.setEditTriggers(QTableWidget.NoEditTriggers)

    header = vista.tabla_receta.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.Stretch)
    vista.tabla_receta.setColumnWidth(1, 80)
    vista.tabla_receta.setColumnWidth(2, 32)
    vista.tabla_receta.setColumnWidth(3, 32)
    vista.tabla_receta.setColumnWidth(4, 60)
    vista.tabla_receta.setColumnWidth(5, 80)

    receta_layout.addWidget(vista.tabla_receta)

    total_grid = QGridLayout()

    total_grid.setColumnStretch(0, 0)
    total_grid.setColumnStretch(1, 0)
    total_grid.setColumnStretch(2, 0)
    total_grid.setColumnStretch(3, 0)
    total_grid.setColumnStretch(4, 1)

    inc_label = QLabel("+-:")
    vista.input_incremento = QLineEdit()
    vista.input_incremento.setText("1")
    vista.input_incremento.setMaximumWidth(60)

    total_label = QLabel("Total:")
    vista.input_cantidad_total = QLineEdit()
    vista.input_cantidad_total.setMaximumWidth(80)

    total_grid.addWidget(inc_label, 0, 0, alignment=Qt.AlignRight)
    total_grid.addWidget(vista.input_incremento, 0, 1, alignment=Qt.AlignLeft)
    total_grid.addWidget(total_label, 0, 2, alignment=Qt.AlignRight)
    total_grid.addWidget(vista.input_cantidad_total, 0, 3, alignment=Qt.AlignLeft)

    receta_layout.addLayout(total_grid)

    pesos_box = QGroupBox("Pesos de óxidos")
    pesos_layout = QHBoxLayout(pesos_box)

    vista.pesos_texto = QTextEdit()
    vista.pesos_pendientes_texto = QTextEdit()

    vista.pesos_texto.setReadOnly(True)
    vista.pesos_pendientes_texto.setReadOnly(True)

    pesos_layout.addWidget(vista.pesos_texto)
    pesos_layout.addWidget(vista.pesos_pendientes_texto)

    fila_sup = QHBoxLayout()
    fila_sup.addWidget(receta_box, 2)
    fila_sup.addWidget(pesos_box, 1)

    botones_layout = QHBoxLayout()

    vista.btn_limpiar = QPushButton("Limpiar")
    vista.btn_guardar = QPushButton("Guardar")
    vista.btn_a_receta = QPushButton("A receta")
    vista.btn_sustituir = QPushButton("Sustituir")
    vista.btn_ajustar = QPushButton("Ajustar")
    vista.btn_deshacer = QPushButton("Deshacer")

    for b in (
        vista.btn_limpiar,
        vista.btn_guardar,
        vista.btn_a_receta,
        vista.btn_sustituir,
        vista.btn_ajustar,
        vista.btn_deshacer,
    ):
        botones_layout.addWidget(b)

    botones_layout.addStretch()

    formula_box = QGroupBox("Fórmula Seger")
    formula_layout = QVBoxLayout(formula_box)
    formula_layout.addLayout(_crear_grid_oxidos(vista))

    col_der.addLayout(fila_sup, 2)
    col_der.addLayout(botones_layout)
    col_der.addWidget(formula_box, 1)

    layout_principal.addWidget(cont_izq, 1)
    layout_principal.addLayout(col_der, 3)


def _crear_grid_oxidos(vista):
    grid = QGridLayout()
    headers = ["Fundentes", "Intermedios", "Formadores"]

    for col, h in enumerate(headers):
        grid.addWidget(QLabel(h), 0, col * 4, 1, 4, alignment=Qt.AlignCenter)

    categorias = ["fundentes", "intermedios", "formadores"]
    max_filas = max(len(vista.OXIDOS[c]) for c in categorias)

    from PySide6.QtWidgets import QLineEdit

    for fila in range(max_filas):
        for col, cat in enumerate(categorias):
            lista = vista.OXIDOS[cat]
            if fila < len(lista):
                ox = lista[fila]

                lbl = QLabel(ox)
                campo = QLineEdit()
                campo.setMaximumWidth(55)

                campo_recalc = QLineEdit()
                campo_recalc.setMaximumWidth(55)
                campo_recalc.setReadOnly(True)

                base_col = col * 4

                grid.addWidget(lbl, fila + 1, base_col, alignment=Qt.AlignRight)
                grid.addWidget(campo, fila + 1, base_col + 1)
                grid.addWidget(campo_recalc, fila + 1, base_col + 2)

                vista.campos_oxidos[ox] = campo
                vista.campos_oxidos_recalc[ox] = campo_recalc

    return grid
