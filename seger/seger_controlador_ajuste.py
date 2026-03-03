
"""
Controlador de ajuste fino para el módulo Seger (versión 01).

Responsabilidad única:
- Activar ajuste fino a partir de una receta existente.
- Permitir edición directa de gramos de materias primas.
- Recalcular fórmula y pendientes en tiempo real.
- Restaurar estado previo (snapshot).

No depende de PySide.
No manipula widgets.
No contiene lógica química.
"""

from seger.seger_logica import receta_a_formula, formula_a_pesos_oxidos


class SegerControladorAjuste:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._activo = False
        self._snapshot = None
        self._pesos_objetivo = None
        self._receta_actual = None

    # ------------------------------------------------------------
    # Estado
    # ------------------------------------------------------------

    def esta_activo(self):
        return self._activo

    # ------------------------------------------------------------
    # Activación
    # ------------------------------------------------------------

    def activar(self, receta: dict, pesos_objetivo: dict, snapshot: dict):
        """
        Activa ajuste fino guardando snapshot y pesos objetivo fijos.
        """
        if not receta:
            return False

        self._snapshot = snapshot
        self._pesos_objetivo = dict(pesos_objetivo)
        self._receta_actual = dict(receta)
        self._activo = True
        return True

    # ------------------------------------------------------------
    # Restauración
    # ------------------------------------------------------------

    def restaurar(self):
        """
        Sale del ajuste fino devolviendo snapshot previo.
        """
        snap = self._snapshot
        self._snapshot = None
        self._pesos_objetivo = None
        self._receta_actual = None
        self._activo = False
        return snap

    # ------------------------------------------------------------
    # Procesamiento de edición directa de gramos
    # ------------------------------------------------------------

    def procesar_receta_editada(self, lineas: list):
        """
        Recibe líneas tipo:
        'Nombre MP: 123.45'
        Devuelve receta, fórmula recalculada y pendientes.
        """
        if not self._activo:
            return None

        nueva_receta = {}

        for linea in lineas:
            if ":" not in linea:
                continue

            nombre, valor = linea.split(":", 1)

            try:
                gramos = float(valor.strip())
            except ValueError:
                continue

            nueva_receta[nombre.strip()] = gramos

        if not nueva_receta:
            return None

        self._receta_actual = nueva_receta

        formula_recalc = receta_a_formula(self.db_path, nueva_receta)
        pesos_actuales = formula_a_pesos_oxidos(formula_recalc)

        pendientes = {}
        for ox, peso_obj in self._pesos_objetivo.items():
            pendientes[ox] = peso_obj - pesos_actuales.get(ox, 0.0)

        return {
            "receta": nueva_receta,
            "formula_recalc": formula_recalc,
            "pendientes": pendientes,
        }

    # ------------------------------------------------------------
    # Accesores
    # ------------------------------------------------------------

    def obtener_receta_actual(self):
        return self._receta_actual or {}
