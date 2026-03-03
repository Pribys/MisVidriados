
"""
Controlador de flujo de cuadratura para el módulo Seger (versión 01).

Responsabilidad única:
- Encapsular interacción con CuadraturaSeger.
- Aplicar materias primas.
- Gestionar deshacer en cuadratura.
- Exponer datos listos para ser pintados por la vista.

No depende de PySide.
No manipula widgets.
No contiene lógica química.
"""

import sqlite3
import json
from seger.seger_cuadratura import CuadraturaSeger
from seger.seger_logica import receta_a_formula


class SegerControladorCuadratura:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.cuadratura = None

    # ------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------

    def iniciar_desde_formula(self, formula_objetivo: dict):
        """
        Crea una nueva cuadratura a partir de una fórmula objetivo.
        """
        from seger.seger_logica import formula_a_pesos_oxidos

        pesos = formula_a_pesos_oxidos(formula_objetivo)
        self.cuadratura = CuadraturaSeger(pesos, formula_objetivo, self.db_path)

        return {
            "pesos_objetivo": pesos,
            "receta": {},
            "pendientes": self.cuadratura.get_pesos_pendientes(),
        }

    # ------------------------------------------------------------
    # Aplicación de materias primas
    # ------------------------------------------------------------

    def aplicar_materia_prima(self, nombre_mp: str):
        if not self.cuadratura:
            return None

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT analisis_oxidos, finalidad FROM materias_primas WHERE nombre = ?",
                (nombre_mp,)
            )
            fila = cur.fetchone()

        if not fila or not fila[0]:
            return None

        try:
            analisis = json.loads(fila[0])
        except Exception:
            return None

        finalidad = (fila[1] or "").strip()

        if finalidad:
            self.cuadratura.aplicar_materia_prima(nombre_mp)
        else:
            pendientes = self.cuadratura.get_pesos_pendientes()
            opciones = [
                ox for ox in analisis.keys()
                if pendientes.get(ox, 0.0) > 0
            ]
            if not opciones:
                return None
            # Si hay múltiples opciones, se deja decisión a la vista
            return {
                "requiere_seleccion": True,
                "opciones": opciones,
                "analisis": analisis,
                "nombre": nombre_mp,
            }

        return self._estado_actual()

    def aplicar_materia_prima_a_oxido(self, nombre_mp: str, oxido: str):
        if not self.cuadratura:
            return None

        self.cuadratura.aplicar_materia_prima_a_oxido(nombre_mp, oxido)
        return self._estado_actual()

    # ------------------------------------------------------------
    # Deshacer
    # ------------------------------------------------------------

    def deshacer(self):
        if not self.cuadratura:
            return None

        self.cuadratura.deshacer()
        return self._estado_actual()

    # ------------------------------------------------------------
    # Estado actual
    # ------------------------------------------------------------

    def _estado_actual(self):
        receta = self.cuadratura.get_receta()
        pendientes = self.cuadratura.get_pesos_pendientes()
        formula_recalc = receta_a_formula(self.db_path, receta)

        return {
            "receta": receta,
            "pendientes": pendientes,
            "formula_recalc": formula_recalc,
        }

    def obtener_receta(self):
        if not self.cuadratura:
            return {}
        return self.cuadratura.get_receta()

    def obtener_pendientes(self):
        if not self.cuadratura:
            return {}
        return self.cuadratura.get_pesos_pendientes()

    def esta_activa(self):
        return self.cuadratura is not None

    def obtener_pesos_objetivo(self):
        if not self.cuadratura:
            return {}
        return self.cuadratura.get_pesos_objetivo()
