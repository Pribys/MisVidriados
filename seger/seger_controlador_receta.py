
"""Controlador de receta (modo receta → fórmula)."""

from seger.seger_logica import receta_a_formula


class SegerControladorReceta:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def modificar(self, receta: dict, fila: int, incremento: float, signo: int):

        if not receta:
            return None

        nombres = list(receta.keys())

        if fila >= len(nombres):
            return None

        nombre = nombres[fila]

        nuevo = receta[nombre] + signo * incremento

        if nuevo < 0:
            nuevo = 0.0

        receta[nombre] = nuevo

        formula = receta_a_formula(self.db_path, receta)

        return {
            "receta": dict(receta),
            "pendientes": {},
            "formula_recalc": formula
        }
