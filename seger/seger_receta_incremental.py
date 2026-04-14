
"""
Gestor de incrementos de receta para el módulo Seger.

Responsabilidad única:
- Aplicar incrementos o decrementos de gramos a una materia prima
  cuando el módulo está en modo receta → fórmula.
- Garantizar que el peso nunca sea negativo.
- Recalcular la fórmula Seger tras la modificación.

No depende de la interfaz.
No altera ninguna lógica química existente.
"""

from seger.seger_logica import receta_a_formula


class RecetaIncrementalManager:

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------

    def aplicar_incremento(self, receta: dict, fila: int, incremento: float, signo: int):
        """
        Aplica incremento o decremento a una fila de receta.

        Parámetros
        ----------
        receta : dict
            Receta actual {materia_prima: gramos}
        fila : int
            Índice de la materia prima en la tabla
        incremento : float
            Cantidad a sumar o restar
        signo : int
            +1 para incremento, -1 para decremento

        Retorna
        -------
        dict con estructura compatible con _pintar_estado
        """

        if not receta:
            return None

        nombres = list(receta.keys())

        if fila >= len(nombres):
            return None

        if incremento < 0:
            incremento = 0.0

        nombre = nombres[fila]
        peso = receta.get(nombre, 0.0)

        nuevo = peso + signo * incremento

        if nuevo < 0:
            nuevo = 0.0

        receta[nombre] = nuevo

        formula = receta_a_formula(self.db_path, receta)

        return {
            "receta": dict(receta),
            "pendientes": {},
            "formula_recalc": formula
        }
