"""
CurrieWidgetEsquinas v07

Corrección clave:
- obtener_datos() NO parsea texto decorativo.
- En modo presentación devuelve los datos internos (_datos).
- En modo edición manual sí parsea texto plano.

Esto permite:
- Mostrar fórmulas en formato Seger sin romper el guardado.
- Mantener una única fuente de verdad (los datos, no el texto).
"""

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

from currie.currie_presentacion_recetas import CurriePresentacionRecetas
from currie.currie_presentacion_formulas import CurriePresentacionFormulas


class CurrieWidgetEsquinas(QWidget):

    ESQUINAS = ("A", "B", "C", "D")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._modo_edicion = False
        self._datos = {e: {"formula": {}, "receta": {}} for e in self.ESQUINAS}
        self._construir_ui()

    # ------------------------------------------------------------

    def _construir_ui(self):
        grid = QGridLayout(self)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        self._formulas = {}
        self._recetas = {}

        for fila, e in enumerate(self.ESQUINAS):
            lbl = QLabel(e)
            lbl.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            grid.addWidget(lbl, fila, 0)

            tf = QTextEdit()
            tf.setMinimumWidth(200)
            grid.addWidget(tf, fila, 1)
            self._formulas[e] = tf

            tr = QTextEdit()
            tr.setMinimumWidth(200)
            grid.addWidget(tr, fila, 2)
            self._recetas[e] = tr

        self.set_modo_edicion(False)

    # ------------------------------------------------------------

    def set_modo_edicion(self, activo: bool):
        self._modo_edicion = activo
        for e in self.ESQUINAS:
            self._formulas[e].setReadOnly(not activo)
            self._recetas[e].setReadOnly(not activo)

        if activo:
            self._mostrar_texto_plano()
        else:
            self._mostrar_formato()

    # ------------------------------------------------------------

    def actualizar(self, formulas: dict, recetas: dict):
        for e in self.ESQUINAS:
            f = formulas.get(e)
            r = recetas.get(e)

            self._datos[e]["formula"] = f.copy() if isinstance(f, dict) else {}
            self._datos[e]["receta"] = r.copy() if isinstance(r, dict) else {}

        self._mostrar_formato()

    # ------------------------------------------------------------

    def obtener_datos(self):
        # Si NO estamos en modo edición, devolver datos internos
        if not self._modo_edicion:
            datos_formula = {
                e: self._datos[e]["formula"].copy()
                for e in self.ESQUINAS
            }
            datos_receta = {
                e: self._datos[e]["receta"].copy()
                for e in self.ESQUINAS
            }
            return datos_formula, datos_receta

        # Modo edición manual: leer texto plano
        datos_formula = {}
        datos_receta = {}

        for e in self.ESQUINAS:
            datos_formula[e] = self._leer_formula_plana(
                self._formulas[e].toPlainText()
            )
            datos_receta[e] = self._leer_receta_plana(
                self._recetas[e].toPlainText()
            )

        return datos_formula, datos_receta

    # ------------------------------------------------------------
    # Presentación
    # ------------------------------------------------------------

    def _mostrar_formato(self):
        for e in self.ESQUINAS:
            self._formulas[e].setPlainText(
                CurriePresentacionFormulas.formula_a_texto(self._datos[e]["formula"])
            )
            self._recetas[e].setPlainText(
                CurriePresentacionRecetas.receta_a_texto(self._datos[e]["receta"])
            )

    def _mostrar_texto_plano(self):
        for e in self.ESQUINAS:
            self._formulas[e].setPlainText(
                "\n".join(f"{ox} {val}" for ox, val in self._datos[e]["formula"].items())
            )
            self._recetas[e].setPlainText(
                "\n".join(f"{mp} {val}" for mp, val in self._datos[e]["receta"].items())
            )

    # ------------------------------------------------------------
    # Lectura de texto plano
    # ------------------------------------------------------------

    @staticmethod
    def _leer_formula_plana(texto: str) -> dict:
        resultado = {}
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            ox, val = linea.split(None, 1)
            resultado[ox] = float(val)
        return resultado

    @staticmethod
    def _leer_receta_plana(texto: str) -> dict:
        resultado = {}
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            nombre, val = linea.rsplit(None, 1)
            resultado[nombre] = float(val)
        return resultado
