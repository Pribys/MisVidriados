"""
Presentación de recetas del módulo Ian Currie.

Responsabilidad:
- Formatear recetas (dict) en texto legible.
- Usable tanto para:
  * recetas de esquinas (A, B, C, D)
  * recetas intermedias (1–35)
  * recetas cargadas desde base de datos

Este módulo:
- NO conoce la vista.
- NO conoce la base de datos.
- NO hace cálculos.
"""


class CurriePresentacionRecetas:

    @staticmethod
    def receta_a_texto(receta: dict, titulo: str | None = None) -> str:
        """
        Convierte una receta en texto formateado.

        receta: dict {materia_prima: porcentaje}
        titulo: opcional, encabezado
        """
        if not receta:
            return ""

        lineas = []
        if titulo:
            lineas.append(titulo)
            lineas.append("-" * len(titulo))

        for mp, valor in sorted(receta.items()):
            lineas.append(f"{mp:20s} {valor:6.2f} %")

        return "\n".join(lineas)
