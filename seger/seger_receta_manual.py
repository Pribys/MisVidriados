
"""
Gestión de receta manual para el modo receta → fórmula.

Responsabilidad:
- Añadir materias primas manualmente
- Mantener historial para deshacer
- Recalcular fórmula Seger
"""

from PySide6.QtWidgets import QInputDialog
from seger.seger_logica import receta_a_formula


class RecetaManualManager:

    def __init__(self):
        self.receta = {}
        self.historial = []

    def agregar(self, parent, db_path, nombre_mp):

        gramos, ok = QInputDialog.getDouble(
            parent,
            "Cantidad de materia prima",
            f"Cantidad de {nombre_mp}:",
            0.0,
            0.0,
            100000.0,
            2
        )

        if not ok:
            return None

        # guardar snapshot
        self.historial.append(self.receta.copy())

        self.receta[nombre_mp] = self.receta.get(nombre_mp, 0.0) + gramos

        formula = receta_a_formula(db_path, self.receta)

        return {
            "receta": dict(self.receta),
            "pendientes": {},
            "formula_recalc": formula
        }

    def deshacer(self, db_path):

        if not self.historial:
            return None

        self.receta = self.historial.pop()

        formula = receta_a_formula(db_path, self.receta)

        return {
            "receta": dict(self.receta),
            "pendientes": {},
            "formula_recalc": formula
        }

    def limpiar(self):
        self.receta.clear()
        self.historial.clear()
