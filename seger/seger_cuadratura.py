"""
Motor de cuadratura de óxidos con materias primas (versión 03).

Incluye:
- Aplicación manual de óxidos.
- Historial acumulativo para deshacer múltiples pasos.
"""

import sqlite3
import json
from copy import deepcopy


class CuadraturaSeger:

    def __init__(self, pesos_objetivo: dict, moles_formula: dict, db_path: str):
        self.db_path = db_path
        self.pesos_objetivo = deepcopy(pesos_objetivo)
        self.pesos_pendientes = deepcopy(pesos_objetivo)
        self.moles_formula = deepcopy(moles_formula)
        self.receta = {}
        self._historial = []

    # ------------------------------------------------------------

    def aplicar_materia_prima(self, nombre_mp: str) -> None:
        analisis, finalidad = self._cargar_mp(nombre_mp)
        if not analisis or not finalidad:
            return

        oxido_objetivo = self._determinar_oxido_objetivo(finalidad, analisis)
        if not oxido_objetivo:
            return

        self._guardar_estado()
        self._aplicar(nombre_mp, analisis, oxido_objetivo)

    # ------------------------------------------------------------

    def aplicar_materia_prima_a_oxido(self, nombre_mp: str, oxido_objetivo: str) -> None:
        analisis, _ = self._cargar_mp(nombre_mp)
        if not analisis:
            return

        if oxido_objetivo not in analisis and oxido_objetivo != "KNaO":
            return

        self._guardar_estado()
        self._aplicar(nombre_mp, analisis, oxido_objetivo)

    # ------------------------------------------------------------
    # Historial
    # ------------------------------------------------------------

    def _guardar_estado(self):
        self._historial.append({
            "pesos_pendientes": deepcopy(self.pesos_pendientes),
            "receta": deepcopy(self.receta),
        })

    def deshacer(self):
        if not self._historial:
            return
        estado = self._historial.pop()
        self.pesos_pendientes = estado["pesos_pendientes"]
        self.receta = estado["receta"]

    # ------------------------------------------------------------

    def _aplicar(self, nombre_mp: str, analisis: dict, oxido_objetivo: str):
        pendiente = self._peso_pendiente_objetivo(oxido_objetivo)
        if pendiente <= 0:
            return

        fraccion = self._fraccion_en_mp(oxido_objetivo, analisis)
        if fraccion <= 0:
            return

        gramos_mp = pendiente / fraccion

        self.receta[nombre_mp] = self.receta.get(nombre_mp, 0.0) + gramos_mp

        for ox, porcentaje in analisis.items():
            aporte = gramos_mp * porcentaje / 100.0
            self.pesos_pendientes[ox] = self.pesos_pendientes.get(ox, 0.0) - aporte

    # ------------------------------------------------------------

    def get_pesos_objetivo(self) -> dict:
        return deepcopy(self.pesos_objetivo)

    def get_pesos_pendientes(self) -> dict:
        return deepcopy(self.pesos_pendientes)

    def get_receta(self) -> dict:
        return deepcopy(self.receta)

    # ------------------------------------------------------------

    def _cargar_mp(self, nombre_mp: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT analisis_oxidos, finalidad FROM materias_primas WHERE nombre = ?",
                (nombre_mp,)
            )
            fila = cur.fetchone()

        if not fila or not fila[0]:
            return None, None

        try:
            analisis = json.loads(fila[0])
        except Exception:
            return None, None

        finalidad = (fila[1] or "").strip()
        return analisis, finalidad

    # ------------------------------------------------------------

    def _determinar_oxido_objetivo(self, finalidad: str, analisis: dict):
        if finalidad == "KNaO":
            return "KNaO"

        if "," in finalidad:
            opciones = [o.strip() for o in finalidad.split(",")]
            return self._resolver_multiple(opciones)

        return finalidad if finalidad in analisis else None

    def _resolver_multiple(self, opciones):
        max_ox = None
        max_moles = -1.0
        for ox in opciones:
            m = self.moles_formula.get(ox, 0.0)
            if m > max_moles:
                max_moles = m
                max_ox = ox
        return max_ox

    def _peso_pendiente_objetivo(self, oxido_objetivo: str) -> float:
        if oxido_objetivo == "KNaO":
            return (
                self.pesos_pendientes.get("K2O", 0.0) +
                self.pesos_pendientes.get("Na2O", 0.0)
            )
        return self.pesos_pendientes.get(oxido_objetivo, 0.0)

    def _fraccion_en_mp(self, oxido_objetivo: str, analisis: dict) -> float:
        if oxido_objetivo == "KNaO":
            k = analisis.get("K2O", 0.0)
            na = analisis.get("Na2O", 0.0)
            return (k + na) / 100.0
        return analisis.get(oxido_objetivo, 0.0) / 100.0
