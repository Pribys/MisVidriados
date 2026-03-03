"""
Presentación de fórmulas Seger para el módulo Currie.

Responsabilidad:
- Formatear una fórmula Seger en tres columnas:
  * Columna 1: XO, X2O
  * Columna 2: X2O3
  * Columna 3: XO2, X2O5
- Devolver texto listo para mostrar.
"""


class CurriePresentacionFormulas:

    COL1 = ("O",)        # XO, X2O (terminan en O)
    COL2 = ("O3",)       # X2O3
    COL3 = ("O2", "O5")  # XO2, X2O5

    @staticmethod
    def formula_a_texto(formula: dict, titulo: str | None = None) -> str:
        if not formula:
            return ""

        col1, col2, col3 = [], [], []

        for ox, val in formula.items():
            if ox.endswith(CurriePresentacionFormulas.COL2):
                col2.append((ox, val))
            elif ox.endswith(CurriePresentacionFormulas.COL3):
                col3.append((ox, val))
            else:
                col1.append((ox, val))

        ancho = 18
        lineas = []

        if titulo:
            lineas.append(titulo)
            lineas.append("-" * len(titulo))

        max_len = max(len(col1), len(col2), len(col3))

        for i in range(max_len):
            c1 = f"{col1[i][0]:<6} {col1[i][1]:6.3f}" if i < len(col1) else " " * ancho
            c2 = f"{col2[i][0]:<6} {col2[i][1]:6.3f}" if i < len(col2) else " " * ancho
            c3 = f"{col3[i][0]:<6} {col3[i][1]:6.3f}" if i < len(col3) else " " * ancho
            lineas.append(f"{c1} | {c2} | {c3}")

        return "\n".join(lineas)
