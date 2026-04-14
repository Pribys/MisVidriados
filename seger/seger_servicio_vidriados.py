
"""Servicio para preparar datos de vidriado."""

import json
from seger.seger_logica import receta_a_formula


def preparar_datos_vidriado(db_path, receta):

    formula = receta_a_formula(db_path, receta)

    total = sum(receta.values()) or 1.0

    receta_porcentajes = {
        mp: round(val / total * 100.0, 1)
        for mp, val in receta.items()
    }

    formula_redondeada = {
        ox: round(valor, 3)
        for ox, valor in formula.items()
    }

    return {
        "receta": json.dumps(receta_porcentajes),
        "formula": json.dumps(formula_redondeada)
    }
