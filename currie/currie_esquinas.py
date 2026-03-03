"""
Gestión de esquinas del experimento Ian Currie (versión 01).

Responsabilidad:
- Mantener el estado del experimento Currie.
- Imponer la secuencia fija de cálculo: C → D → A → B.
- Construir fórmulas Seger objetivo en el espacio de óxidos.
- Almacenar fórmulas Seger y recetas devueltas desde Seger.

Este archivo:
- NO depende de PySide.
- NO conoce materias primas.
- NO calcula recetas.
- NO accede a base de datos.
"""

from copy import deepcopy


class CurrieEsquinas:
    """
    Gestor de las cuatro esquinas de un experimento Currie.
    """

    ORDEN = ("C", "D", "A", "B")

    def __init__(self, delta_sio2: float, delta_al2o3: float):
        """
        Inicializa el experimento Currie.

        Parámetros:
        - delta_sio2: incremento total de SiO2
        - delta_al2o3: incremento total de Al2O3
        """
        self.delta_sio2 = float(delta_sio2)
        self.delta_al2o3 = float(delta_al2o3)

        self._estado = "C"

        self.formulas = {k: None for k in self.ORDEN}
        self.recetas = {k: None for k in self.ORDEN}

    def esquina_actual(self) -> str | None:
        """Devuelve la esquina que debe calcularse a continuación."""
        return self._estado

    def experimento_completo(self) -> bool:
        """Indica si el experimento está completo."""
        return self._estado is None

    def get_formula_objetivo(self) -> dict | None:
        """
        Devuelve la fórmula Seger objetivo para la esquina actual.
        """
        if self._estado == "C":
            return None

        if self._estado == "D":
            return self._sumar_sio2(self.formulas["C"], self.delta_sio2)

        if self._estado == "A":
            return self._sumar_al2o3(self.formulas["C"], self.delta_al2o3)

        if self._estado == "B":
            return self._sumar_sio2(self.formulas["A"], self.delta_sio2)

        return None

    def registrar_resultado(self, formula: dict, receta: dict) -> None:
        """
        Registra la fórmula y receta calculadas para la esquina actual.
        """
        if self._estado is None:
            return

        self.formulas[self._estado] = deepcopy(formula)
        self.recetas[self._estado] = deepcopy(receta)
        self._avanzar_estado()

    def _avanzar_estado(self) -> None:
        idx = self.ORDEN.index(self._estado)
        self._estado = self.ORDEN[idx + 1] if idx + 1 < len(self.ORDEN) else None

    @staticmethod
    def _sumar_sio2(formula_base: dict, delta: float) -> dict:
        nueva = deepcopy(formula_base)
        nueva["SiO2"] = nueva.get("SiO2", 0.0) + delta
        return nueva

    @staticmethod
    def _sumar_al2o3(formula_base: dict, delta: float) -> dict:
        nueva = deepcopy(formula_base)
        nueva["Al2O3"] = nueva.get("Al2O3", 0.0) + delta
        return nueva
