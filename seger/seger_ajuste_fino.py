
"""
Motor de Ajuste Fino para el módulo Seger (versión 02).

Responsabilidad única:
- Gestionar el estado de ajuste fino como capa reversible.
- Recalcular receta -> fórmula -> pesos -> pendientes en tiempo real.
- Restaurar exactamente el estado previo al ajuste fino.

No depende de CuadraturaSeger.
No contiene lógica de interfaz.
No altera cálculos químicos existentes.
"""

from seger.seger_logica import receta_a_formula, formula_a_pesos_oxidos


class AjusteFinoSeger:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.activo = False

        # Snapshot previo al ajuste fino
        self._snapshot = None

        # Datos fijos durante ajuste fino
        self._pesos_objetivo = None
        self._formula_objetivo = None

        # Resultados recalculados en tiempo real
        self._receta_actual = None
        self._formula_recalc = None
        self._pendientes = None

    # ------------------------------------------------------------

    def activar(self, receta: dict, pesos_objetivo: dict, formula_objetivo: dict, snapshot: dict):
        """
        Activa el modo ajuste fino guardando snapshot completo.
        """
        if not receta:
            return False

        self._snapshot = snapshot
        self._pesos_objetivo = dict(pesos_objetivo)
        self._formula_objetivo = dict(formula_objetivo)
        self._receta_actual = dict(receta)

        # Estado inicial coherente con lo que ya se ve en pantalla
        self._formula_recalc = receta_a_formula(self.db_path, self._receta_actual)
        self._pendientes = self._calcular_pendientes(self._formula_recalc)

        self.activo = True
        return True

    # ------------------------------------------------------------

    def desactivar(self):
        """
        Desactiva ajuste fino sin restaurar snapshot.
        """
        self.activo = False

    # ------------------------------------------------------------

    def restaurar_snapshot(self):
        """
        Devuelve el snapshot guardado al entrar en ajuste fino.
        """
        self.activo = False
        return self._snapshot

    # ------------------------------------------------------------

    def procesar_porcentajes(self, lineas_mp: list, lineas_pct: list, total: float | None):
        """
        Procesa porcentajes editados y recalcula todo en tiempo real.
        """
        if not self.activo:
            return None

        if len(lineas_mp) != len(lineas_pct):
            return None

        nombres = []
        porcentajes = []

        for linea_mp, linea_pct in zip(lineas_mp, lineas_pct):
            if ":" not in linea_mp:
                continue

            nombre = linea_mp.split(":", 1)[0].strip()

            try:
                valor = float(linea_pct.replace("%", "").strip())
            except ValueError:
                continue

            nombres.append(nombre)
            porcentajes.append(valor)

        if not porcentajes:
            return None

        suma = sum(porcentajes)
        if suma == 0:
            return None

        porcentajes_norm = [p / suma for p in porcentajes]

        if total is None:
            total = sum(self._receta_actual.values())

        nueva_receta = {}
        for nombre, p in zip(nombres, porcentajes_norm):
            nueva_receta[nombre] = p * total

        self._receta_actual = nueva_receta

        # Recalcular fórmula y pendientes
        self._formula_recalc = receta_a_formula(self.db_path, self._receta_actual)
        self._pendientes = self._calcular_pendientes(self._formula_recalc)

        return {
            "receta": self._receta_actual,
            "formula_recalc": self._formula_recalc,
            "pendientes": self._pendientes,
        }

    # ------------------------------------------------------------

    def _calcular_pendientes(self, formula_recalc: dict):
        """
        Calcula pesos pendientes respecto a los pesos objetivo fijos.
        """
        pesos_actuales = formula_a_pesos_oxidos(formula_recalc)

        pendientes = {}
        for ox, peso_obj in self._pesos_objetivo.items():
            pendientes[ox] = peso_obj - pesos_actuales.get(ox, 0.0)

        return pendientes

    # ------------------------------------------------------------

    def get_formula_recalc(self):
        return self._formula_recalc

    def get_pendientes(self):
        return self._pendientes

    def get_receta_actual(self):
        return self._receta_actual
