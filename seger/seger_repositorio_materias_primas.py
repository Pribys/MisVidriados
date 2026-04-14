
"""Repositorio de materias primas."""

import sqlite3


def listar_materias_primas(db_path):

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT nombre FROM materias_primas ORDER BY nombre")
        return [r[0] for r in cur.fetchall()]
