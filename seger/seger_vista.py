
"""
Vista del módulo Seger (versión 38).

Corrección:
- Limpia el símbolo % al convertir los porcentajes para guardado.
- No se modifica ninguna otra funcionalidad.
"""

import sqlite3
import json
from PySide6.QtWidgets import (
    QWidget, QInputDialog, QTableWidgetItem, QPushButton
)

from seger.seger_logica import receta_a_formula
from seger.seger_vista_ui import construir_ui
from seger.seger_vista_presentacion import (
    formatear_receta,
    formatear_pesos_pendientes
)

from seger.seger_controlador_cuadratura import SegerControladorCuadratura
from seger.seger_controlador_ajuste import SegerControladorAjuste


class SegerVista(QWidget):

    OXIDOS = {
        "fundentes": ["Li2O", "Na2O", "K2O", "MgO", "CaO", "SrO", "BaO", "ZnO", "PbO"],
        "intermedios": ["Al2O3", "B2O3", "Fe2O3"],
        "formadores": ["SiO2", "P2O5", "TiO2", "ZrO2", "SnO2"],
    }

    def __init__(self, db_path: str, vidriados_vista=None):
        super().__init__()

        self.db_path = db_path
        self.vidriados_vista = vidriados_vista

        self.campos_oxidos = {}
        self.campos_oxidos_recalc = {}
        self.formula_original = {}
        self._estado_actual = None

        self.ctrl_cuadratura = SegerControladorCuadratura(self.db_path)
        self.ctrl_ajuste = SegerControladorAjuste(self.db_path)

        construir_ui(self)
        self._conectar()
        self._cargar_materias_primas()

    def _conectar(self):
        self.lista_materias.itemDoubleClicked.connect(self._usar_materia_prima)
        self.btn_a_formula.clicked.connect(self._calcular_formula)
        self.btn_a_receta.clicked.connect(self._iniciar_cuadratura)
        self.btn_deshacer.clicked.connect(self._deshacer)
        self.btn_ajustar.clicked.connect(self._activar_ajuste)
        self.btn_limpiar.clicked.connect(self._limpiar)
        self.btn_guardar.clicked.connect(self._guardar_vidriado)
        self.input_cantidad_total.textChanged.connect(self._recalcular_cantidades)

    def _iniciar_cuadratura(self):
        self.formula_original = {
            ox: float(campo.text())
            for ox, campo in self.campos_oxidos.items()
            if campo.text().strip()
        }
        datos = self.ctrl_cuadratura.iniciar_desde_formula(self.formula_original)
        self.pesos_texto.setPlainText(
            "\n".join(f"{ox}: {v:.2f}" for ox, v in datos["pesos_objetivo"].items())
        )
        self._pintar_estado(datos)

    def _usar_materia_prima(self, item):
        if not self.ctrl_cuadratura.esta_activa():
            return
        resultado = self.ctrl_cuadratura.aplicar_materia_prima(item.text())
        if not resultado:
            return
        if resultado.get("requiere_seleccion"):
            oxido, ok = QInputDialog.getItem(
                self,
                "Seleccionar óxido",
                f"¿Qué óxido quieres cuadrar con {resultado['nombre']}?",
                resultado["opciones"],
                0,
                False
            )
            if ok and oxido:
                resultado = self.ctrl_cuadratura.aplicar_materia_prima_a_oxido(
                    resultado["nombre"], oxido
                )
            else:
                return
        self._pintar_estado(resultado)

    def _activar_ajuste(self):
        if not self.ctrl_cuadratura.esta_activa():
            return
        receta = self.ctrl_cuadratura.obtener_receta()
        pesos_obj = self.ctrl_cuadratura.obtener_pesos_objetivo()
        snapshot = {"estado": self.ctrl_cuadratura._estado_actual()}
        ok = self.ctrl_ajuste.activar(receta, pesos_obj, snapshot)
        if not ok:
            return
        self.lista_materias.setEnabled(False)

    def _ajustar_fila(self, fila: int, factor: float):
        if not self.ctrl_ajuste.esta_activo():
            return
        receta = self.ctrl_ajuste.obtener_receta_actual()
        nombres = list(receta.keys())
        if fila >= len(nombres):
            return
        receta[nombres[fila]] *= factor
        datos = self.ctrl_ajuste.procesar_receta_editada(
            [f"{mp}: {val}" for mp, val in receta.items()]
        )
        if datos:
            self._pintar_estado(datos)

    def _deshacer(self):
        if self.ctrl_ajuste.esta_activo():
            snap = self.ctrl_ajuste.restaurar()
            self.lista_materias.setEnabled(True)
            self._pintar_estado(snap["estado"])
            return
        estado = self.ctrl_cuadratura.deshacer()
        if estado:
            self._pintar_estado(estado)

    def _pintar_estado(self, datos):
        self._estado_actual = datos
        receta = datos.get("receta", {})
        pendientes = datos.get("pendientes", {})
        formula_recalc = datos.get("formula_recalc", {})
        total_deseado = self._leer_total()
        nombres, pesos, pcts, cants = formatear_receta(receta, total_deseado)
        self.tabla_receta.setRowCount(len(nombres))
        for fila, (mp, peso, pct, cant) in enumerate(zip(nombres, pesos, pcts, cants)):
            self.tabla_receta.setItem(fila, 0, QTableWidgetItem(mp))
            self.tabla_receta.setItem(fila, 1, QTableWidgetItem(peso))
            btn_mas = QPushButton("+")
            btn_menos = QPushButton("-")
            btn_mas.clicked.connect(lambda _, f=fila: self._ajustar_fila(f, 1.01))
            btn_menos.clicked.connect(lambda _, f=fila: self._ajustar_fila(f, 0.99))
            self.tabla_receta.setCellWidget(fila, 2, btn_mas)
            self.tabla_receta.setCellWidget(fila, 3, btn_menos)
            self.tabla_receta.setItem(fila, 4, QTableWidgetItem(pct))
            self.tabla_receta.setItem(fila, 5, QTableWidgetItem(cant))
        self.pesos_pendientes_texto.setPlainText(
            formatear_pesos_pendientes(pendientes)
        )
        for ox, campo in self.campos_oxidos_recalc.items():
            if ox in formula_recalc:
                campo.setText(f"{formula_recalc[ox]:.3f}")
            else:
                campo.clear()

    def _recalcular_cantidades(self):
        if self._estado_actual:
            self._pintar_estado(self._estado_actual)

    def _leer_total(self):
        try:
            return float(self.input_cantidad_total.text())
        except ValueError:
            return None

    def _limpiar(self):
        self.input_cantidad_total.blockSignals(True)
        self._estado_actual = None
        self.formula_original = {}
        self.tabla_receta.setRowCount(0)
        for campo in self.campos_oxidos.values():
            campo.clear()
        for campo in self.campos_oxidos_recalc.values():
            campo.clear()
        self.pesos_texto.clear()
        self.pesos_pendientes_texto.clear()
        self.input_cantidad_total.clear()
        self.input_cantidad_total.blockSignals(False)
        self.ctrl_cuadratura = SegerControladorCuadratura(self.db_path)
        self.ctrl_ajuste = SegerControladorAjuste(self.db_path)
        self.lista_materias.setEnabled(True)

    def _guardar_vidriado(self):
        if self.ctrl_ajuste.esta_activo():
            receta = self.ctrl_ajuste.obtener_receta_actual()
        else:
            receta = self.ctrl_cuadratura.obtener_receta()

        if not receta or not self.vidriados_vista:
            return

        formula = receta_a_formula(self.db_path, receta)

        nombres, _, porcentajes, _ = formatear_receta(receta, None)

        receta_porcentajes = {
            mp: float(pct.replace("%", "").strip())
            for mp, pct in zip(nombres, porcentajes)
        }

        formula_redondeada = {
            ox: round(valor, 3)
            for ox, valor in formula.items()
        }

        datos = {
            "receta": json.dumps(receta_porcentajes),
            "formula": json.dumps(formula_redondeada)
        }

        self.vidriados_vista.controlador.crear_nuevo(
            parent=self.vidriados_vista,
            datos=datos
        )

    def _calcular_formula(self):
        receta = self.ctrl_cuadratura.obtener_receta()
        formula = receta_a_formula(self.db_path, receta)
        for campo in self.campos_oxidos.values():
            campo.clear()
        for ox, val in formula.items():
            if ox in self.campos_oxidos:
                self.campos_oxidos[ox].setText(f"{val:.3f}")

    def _cargar_materias_primas(self):
        self.lista_materias.clear()
        with sqlite3.connect(self.db_path) as conn:
            for (nombre,) in conn.execute(
                "SELECT nombre FROM materias_primas ORDER BY nombre"
            ):
                self.lista_materias.addItem(nombre)
