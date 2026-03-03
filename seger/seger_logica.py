
"""
Lógica del módulo de cálculos Seger (versión 03).

CONTIENE TODA LA FUNCIONALIDAD ACUMULADA:
- Conversión receta -> fórmula Seger.
- Conversión fórmula Seger -> pesos de óxidos.

Este archivo SUSTITUYE completamente a seger_logica.py
en el proyecto real (el usuario eliminará la numeración).
"""

import sqlite3
import json

# ---------------- Pesos moleculares ----------------

PESOS_MOLECULARES = {
    "Li2O": 29.88,
    "Na2O": 61.98,
    "K2O": 94.20,
    "MgO": 40.30,
    "CaO": 56.08,
    "SrO": 103.62,
    "BaO": 153.33,
    "ZnO": 81.38,
    "PbO": 223.20,
    "Al2O3": 101.96,
    "B2O3": 69.62,
    "Fe2O3": 159.69,
    "SiO2": 60.08,
    "P2O5": 141.94,
    "TiO2": 79.87,
    "ZrO2": 123.22,
    "SnO2": 150.71,
}

FUNDENTES = {
    "Li2O", "Na2O", "K2O", "MgO", "CaO",
    "SrO", "BaO", "ZnO", "PbO"
}

# ---------------- Receta -> Fórmula ----------------

def receta_a_formula(db_path: str, receta: dict) -> dict:
    """
    Convierte una receta (materia prima -> peso) en fórmula Seger.

    Parámetros:
    - db_path: ruta a la base de datos.
    - receta: dict {materia_prima: peso}

    Retorna:
    - dict {oxido: moles_normalizados}
    """

    # Cargar análisis químicos
    analisis_mp = {}
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for mp in receta.keys():
            cur.execute(
                "SELECT analisis_oxidos FROM materias_primas WHERE nombre = ?",
                (mp,)
            )
            fila = cur.fetchone()
            if not fila or not fila[0]:
                continue
            try:
                analisis_mp[mp] = json.loads(fila[0])
            except Exception:
                continue

    # Sumar gramos de óxidos
    gramos_oxidos = {}
    for mp, peso_mp in receta.items():
        analisis = analisis_mp.get(mp)
        if not analisis:
            continue
        for ox, porcentaje in analisis.items():
            gramos = peso_mp * porcentaje / 100.0
            gramos_oxidos[ox] = gramos_oxidos.get(ox, 0.0) + gramos

    # Convertir a moles
    moles_oxidos = {}
    for ox, gramos in gramos_oxidos.items():
        pm = PESOS_MOLECULARES.get(ox)
        if pm:
            moles_oxidos[ox] = gramos / pm

    # Normalizar por fundentes
    suma_fundentes = sum(
        m for ox, m in moles_oxidos.items() if ox in FUNDENTES
    )
    if suma_fundentes == 0:
        return {}

    return {
        ox: m / suma_fundentes
        for ox, m in moles_oxidos.items()
    }

# ---------------- Fórmula -> Pesos de óxidos ----------------

def formula_a_pesos_oxidos(formula: dict) -> dict:
    """
    Convierte una fórmula Seger (óxido -> moles) en pesos de óxidos.

    Parámetros:
    - formula: dict {oxido: moles}

    Retorna:
    - dict {oxido: gramos}
    """

    pesos = {}
    for ox, moles in formula.items():
        try:
            m = float(moles)
        except Exception:
            continue
        pm = PESOS_MOLECULARES.get(ox)
        if pm:
            pesos[ox] = m * pm
    return pesos
