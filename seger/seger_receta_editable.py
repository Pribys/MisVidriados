
"""
Módulo auxiliar para permitir edición manual reactiva de la receta.

Responsabilidad única:
- Convertir texto editable en dict de receta.
- Recalcular fórmula Seger.
- Reconstruir objeto CuadraturaSeger coherente.

No contiene lógica de interfaz.
No altera cálculos químicos existentes.
"""

from seger.seger_logica import receta_a_formula, formula_a_pesos_oxidos
from seger.seger_cuadratura import CuadraturaSeger


def texto_a_receta(texto: str) -> dict:
    receta = {}
    for linea in texto.splitlines():
        if ":" not in linea:
            continue
        nombre, valor = linea.split(":", 1)
        try:
            receta[nombre.strip()] = float(valor.strip())
        except ValueError:
            continue
    return receta


def reconstruir_cuadratura(db_path: str, texto_receta: str):
    receta = texto_a_receta(texto_receta)
    if not receta:
        return None

    formula = receta_a_formula(db_path, receta)
    if not formula:
        return None

    pesos = formula_a_pesos_oxidos(formula)
    return CuadraturaSeger(pesos, formula, db_path)
