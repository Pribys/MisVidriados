"""
Cálculo de recetas intermedias del método Ian Currie.

Responsabilidad:
- Calcular cualquiera de los 35 vidriados de un experimento Currie
  a partir de las recetas de las cuatro esquinas A, B, C y D.
- Devolver la receta final normalizada a porcentaje.

Convenciones:
- Numeración de vidriados: 1–35 (7 filas x 5 columnas).
- Esquinas:
    A = 1   (arriba izquierda)
    B = 5   (arriba derecha)
    C = 31  (abajo izquierda)
    D = 35  (abajo derecha)
- Mezclas basadas en el diagrama clásico de 20 partes.
"""


class CurrieMezclas:
    """
    Motor de cálculo de mezclas Currie.
    """

    TOTAL_PARTES = 20

    def __init__(self, receta_A: dict, receta_B: dict, receta_C: dict, receta_D: dict):
        self.recetas = {
            "A": receta_A,
            "B": receta_B,
            "C": receta_C,
            "D": receta_D,
        }

    # ------------------------------------------------------------

    def calcular(self, numero: int) -> dict:
        """
        Calcula la receta del vidriado indicado (1–35).

        Devuelve:
        - dict {materia_prima: porcentaje}
        """
        if numero < 1 or numero > 35:
            raise ValueError("El número de vidriado debe estar entre 1 y 35.")

        partes = self._partes_vidriado(numero)

        receta_final = {}

        for esquina, peso in partes.items():
            receta_esq = self.recetas[esquina]
            for mp, valor in receta_esq.items():
                receta_final[mp] = receta_final.get(mp, 0.0) + valor * peso

        return self._normalizar(receta_final)

    # ------------------------------------------------------------

    def _normalizar(self, receta: dict) -> dict:
        total = sum(receta.values())
        if total == 0:
            return {}

        return {
            mp: (valor / total) * 100.0
            for mp, valor in receta.items()
        }

    # ------------------------------------------------------------

    def _partes_vidriado(self, numero: int) -> dict:
        """
        Devuelve las partes A, B, C y D según el diagrama Currie.
        """
        fila = (numero - 1) // 5
        col = (numero - 1) % 5

        # Interpolación vertical (de A/B a C/D)
        partes_vertical = [
            (20, 0),
            (16, 4),
            (14, 6),
            (10, 10),
            (7, 14),
            (4, 16),
            (0, 20),
        ]

        arriba, abajo = partes_vertical[fila]

        # Interpolación horizontal
        partes_horizontal = [
            (arriba, 0),
            (arriba - arriba * col / 4, arriba * col / 4),
            (arriba / 2, arriba / 2),
            (arriba * col / 4, arriba - arriba * col / 4),
            (0, arriba),
        ]

        A = partes_horizontal[col][0]
        B = partes_horizontal[col][1]

        partes_horizontal_inf = [
            (abajo, 0),
            (abajo - abajo * col / 4, abajo * col / 4),
            (abajo / 2, abajo / 2),
            (abajo * col / 4, abajo - abajo * col / 4),
            (0, abajo),
        ]

        C = partes_horizontal_inf[col][0]
        D = partes_horizontal_inf[col][1]

        return {
            "A": A,
            "B": B,
            "C": C,
            "D": D,
        }
