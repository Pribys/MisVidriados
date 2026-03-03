"""
Cálculo de recetas intermedias (1–35) para un experimento Currie.

Responsabilidad:
- Calcular la receta de cualquier vidriado del experimento
  a partir de las cuatro esquinas.
- Devolver resultados normalizados a porcentaje.
"""

from currie.currie_mezclas import CurrieMezclas


class CurrieRecetas:

    def __init__(self, recetas_esquinas: dict):
        """
        recetas_esquinas: dict con claves 'A','B','C','D'
        """
        self._mezclas = CurrieMezclas(
            recetas_esquinas["A"],
            recetas_esquinas["B"],
            recetas_esquinas["C"],
            recetas_esquinas["D"],
        )

    def calcular(self, numero: int) -> dict:
        return self._mezclas.calcular(numero)
