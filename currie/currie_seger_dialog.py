"""
Diálogo independiente de Seger para el módulo Currie (versión 01).

Responsabilidad:
- Abrir SegerVista en una ventana independiente.
- Precargar una fórmula Seger completa (incluidos fundentes).
- Reutilizar el botón 'Guardar' como 'A Currie'.
- Devolver fórmula y receta al módulo Currie.
- Cerrar automáticamente la ventana al finalizar.

Este archivo:
- NO modifica SegerVista.
- NO contiene lógica Currie.
- NO guarda en base de datos.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout
from seger.seger_vista import SegerVista


class CurrieSegerDialog(QDialog):
    """
    Diálogo independiente que envuelve SegerVista para el flujo Currie.
    """

    def __init__(self, db_path: str, formula_inicial: dict | None, on_resultado):
        super().__init__()
        self._on_resultado = on_resultado

        self.setWindowTitle("Cálculo Seger (método Ian Currie)")
        self.resize(900, 650)

        layout = QVBoxLayout(self)
        self.seger = SegerVista(db_path)
        layout.addWidget(self.seger)

        # Adaptar botón Guardar
        self.seger.btn_guardar.setText("A Currie")
        self.seger.btn_guardar.clicked.disconnect()
        self.seger.btn_guardar.clicked.connect(self._enviar_y_cerrar)

        # Precargar fórmula completa
        self._precargar_formula(formula_inicial)

    # ------------------------------------------------------------

    def _precargar_formula(self, formula: dict | None):
        # Limpiar todos los campos
        for campo in self.seger.campos_oxidos.values():
            campo.clear()

        if not formula:
            return

        for ox, val in formula.items():
            if ox in self.seger.campos_oxidos:
                self.seger.campos_oxidos[ox].setText(f"{val:.3f}")

    # ------------------------------------------------------------

    def _enviar_y_cerrar(self):
        # --- Extraer receta en porcentaje ---
        receta = {}
        lineas_pct = self.seger.receta_pct_texto.toPlainText().splitlines()
        lineas_mp = self.seger.receta_texto.toPlainText().splitlines()

        if len(lineas_pct) == len(lineas_mp):
            for lp, lm in zip(lineas_pct, lineas_mp):
                if ":" not in lm:
                    continue
                mp = lm.split(":", 1)[0].strip()
                try:
                    receta[mp] = float(lp.replace("%", "").strip())
                except ValueError:
                    continue

        # --- Extraer fórmula ---
        formula = {}

        # Preferir recalculada
        for ox, campo in self.seger.campos_oxidos_recalc.items():
            txt = campo.text().strip()
            if txt:
                try:
                    formula[ox] = float(txt)
                except ValueError:
                    pass

        # Si no hay recalculada, usar original
        if not formula:
            for ox, campo in self.seger.campos_oxidos.items():
                txt = campo.text().strip()
                if txt:
                    try:
                        formula[ox] = float(txt)
                    except ValueError:
                        pass

        if formula and receta:
            self._on_resultado(formula, receta)

        self.accept()
