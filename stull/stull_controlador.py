# -----------------------------------------------------------------------------
# 09_stull_controlador.py
#
# Controlador del módulo Stull.
#
# Responsabilidad:
# - Leer vidriados desde la base de datos
# - Leer experimentos Currie
# - Generar las 35 fórmulas Currie
# - Unificar estructura para el gráfico Stull
#
# Modificación v09:
# - Se añade el campo "brillo" a los puntos provenientes de BD
# - Los puntos Currie incluyen brillo=None
#
# Encapsulado. No depende de Qt.
# -----------------------------------------------------------------------------

import sqlite3
import json
from typing import List, Dict, Any


class StullControlador:
    """Controlador del módulo Stull."""

    PARTS_MATRIX = [
        (5, 0, 0, 0), (6, 2, 0, 0), (3, 3, 0, 0), (2, 6, 0, 0), (0, 5, 0, 0),
        (5, 0, 1, 0), (15, 5, 3, 1), (9, 9, 3, 3), (5, 15, 1, 3), (0, 5, 0, 1),
        (5, 0, 2, 0), (12, 4, 6, 2), (6, 6, 6, 6), (4, 12, 2, 6), (0, 5, 0, 2),
        (5, 0, 3, 0), (9, 3, 9, 3), (3, 3, 9, 9), (3, 9, 3, 9), (0, 5, 0, 3),
        (5, 0, 4, 0), (6, 2, 12, 4), (3, 3, 12, 12), (2, 6, 4, 12), (0, 5, 0, 4),
        (5, 0, 5, 0), (3, 1, 15, 5), (1, 1, 15, 15), (1, 3, 5, 15), (0, 5, 0, 5),
        (0, 0, 5, 0), (0, 0, 6, 2), (0, 0, 3, 3), (0, 0, 2, 6), (0, 0, 0, 5),
    ]

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------------
    # VIDRIADOS BASE
    # ------------------------------------------------------------------

    def obtener_vidriados(self) -> List[Dict[str, Any]]:
        """Devuelve todos los vidriados con estructura unificada."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT id, codigo, temperatura, formula, brillo
                FROM vidriados
                ORDER BY codigo
            """)
            filas = cur.fetchall()

        resultado = []

        for row in filas:
            formula = self._parse_formula(row["formula"])
            if not formula:
                continue

            resultado.append({
                "codigo": row["codigo"],
                "sio2": formula.get("SiO2", 0.0),
                "al2o3": formula.get("Al2O3", 0.0),
                "temperatura": row["temperatura"],
                "brillo": row["brillo"],
                "tipo": "bd",
                "formula": formula
            })

        return resultado

    # ------------------------------------------------------------------
    # EXPERIMENTOS CURRIE
    # ------------------------------------------------------------------

    def obtener_experimentos_currie(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nombre
                FROM currie_experimentos
                ORDER BY nombre
            """)
            filas = cur.fetchall()

        return [dict(row) for row in filas]

    def generar_currie(self, experimento_id: int) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT nombre, formula_A, formula_B,
                       formula_C, formula_D, temperatura
                FROM currie_experimentos
                WHERE id = ?
            """, (experimento_id,))
            row = cur.fetchone()

        if not row:
            return []

        nombre = row["nombre"]
        temp = row["temperatura"]

        A = self._parse_formula(row["formula_A"])
        B = self._parse_formula(row["formula_B"])
        C = self._parse_formula(row["formula_C"])
        D = self._parse_formula(row["formula_D"])

        if not all([A, B, C, D]):
            return []

        puntos = []

        for idx, (a, b, c, d) in enumerate(self.PARTS_MATRIX, start=1):
            formula = self._mezcla_lineal(A, B, C, D, a, b, c, d)

            puntos.append({
                "codigo": f"{nombre}-{idx:02d}",
                "sio2": formula.get("SiO2", 0.0),
                "al2o3": formula.get("Al2O3", 0.0),
                "temperatura": temp,
                "brillo": None,
                "tipo": "currie",
                "formula": formula
            })

        return puntos

    # ------------------------------------------------------------------
    # AUXILIARES
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_formula(texto: str) -> Dict[str, float]:
        try:
            data = json.loads(texto) if texto else {}
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _mezcla_lineal(A, B, C, D, a, b, c, d):
        total = a + b + c + d
        if total == 0:
            return {}

        resultado = {}
        oxidos = set(A) | set(B) | set(C) | set(D)

        for ox in oxidos:
            valor = (
                a * A.get(ox, 0.0) +
                b * B.get(ox, 0.0) +
                c * C.get(ox, 0.0) +
                d * D.get(ox, 0.0)
            ) / total
            resultado[ox] = valor

        return resultado
