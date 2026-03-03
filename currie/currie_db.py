
"""
Acceso a base de datos para experimentos Ian Currie.

Responsabilidad:
- Lectura de experimentos (ya existente).
- CRUD completo sobre la tabla currie_experimentos.
- Serialización/deserialización JSON de recetas, fórmulas e imágenes.

Este módulo:
- NO conoce la interfaz.
- NO realiza cálculos Currie.
"""

import sqlite3
import json


class CurrieDB:

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------

    def _columnas_disponibles(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(currie_experimentos)")
        cols = [fila[1] for fila in cur.fetchall()]
        conn.close()
        return cols

    # ------------------------------------------------------------
    # READ
    # ------------------------------------------------------------

    def listar_experimentos(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM currie_experimentos ORDER BY nombre")
        datos = cur.fetchall()
        conn.close()
        return datos

    def cargar_experimento(self, exp_id: int):
        columnas = self._columnas_disponibles()

        base_cols = [
            "fundentes", "delta_sio2", "delta_al2o3",
            "receta_A", "receta_B", "receta_C", "receta_D",
            "formula_A", "formula_B", "formula_C", "formula_D",
        ]

        opcionales = [
            "fecha", "temperatura", "meseta", "soporte", "notas", "imagenes"
        ]

        cols = base_cols + [c for c in opcionales if c in columnas]

        sql = "SELECT " + ", ".join(cols) + " FROM currie_experimentos WHERE id = ?"

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(sql, (exp_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        data = dict(zip(cols, row))

        return {
            "fundentes": data["fundentes"],
            "delta_sio2": data["delta_sio2"],
            "delta_al2o3": data["delta_al2o3"],
            "recetas": {
                "A": json.loads(data["receta_A"]),
                "B": json.loads(data["receta_B"]),
                "C": json.loads(data["receta_C"]),
                "D": json.loads(data["receta_D"]),
            },
            "formulas": {
                "A": json.loads(data["formula_A"]),
                "B": json.loads(data["formula_B"]),
                "C": json.loads(data["formula_C"]),
                "D": json.loads(data["formula_D"]),
            },
            "fecha": data.get("fecha", ""),
            "temperatura": data.get("temperatura", ""),
            "meseta": data.get("meseta", ""),
            "soporte": data.get("soporte", ""),
            "comentarios": data.get("notas", ""),
            "imagenes": json.loads(data["imagenes"]) if data.get("imagenes") else [],
        }

    # ------------------------------------------------------------
    # CREATE / UPDATE
    # ------------------------------------------------------------

    def crear_experimento(self, nombre: str, datos: dict) -> int:
        sql = """
        INSERT INTO currie_experimentos (
            nombre, fecha, fundentes, delta_sio2, delta_al2o3,
            receta_A, receta_B, receta_C, receta_D,
            formula_A, formula_B, formula_C, formula_D,
            temperatura, meseta, soporte, notas, imagenes
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """

        valores = (
            nombre,
            datos.get("fecha", ""),
            datos["fundentes"],
            datos["delta_sio2"],
            datos["delta_al2o3"],
            json.dumps(datos["recetas"]["A"]),
            json.dumps(datos["recetas"]["B"]),
            json.dumps(datos["recetas"]["C"]),
            json.dumps(datos["recetas"]["D"]),
            json.dumps(datos["formulas"]["A"]),
            json.dumps(datos["formulas"]["B"]),
            json.dumps(datos["formulas"]["C"]),
            json.dumps(datos["formulas"]["D"]),
            datos.get("temperatura", ""),
            datos.get("meseta", ""),
            datos.get("soporte", ""),
            datos.get("comentarios", ""),
            json.dumps(datos.get("imagenes", [])),
        )

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(sql, valores)
        conn.commit()
        exp_id = cur.lastrowid
        conn.close()

        return exp_id

    def actualizar_experimento(self, exp_id: int, nombre: str, datos: dict) -> None:
        sql = """
        UPDATE currie_experimentos SET
            nombre = ?,
            fecha = ?,
            fundentes = ?,
            delta_sio2 = ?,
            delta_al2o3 = ?,
            receta_A = ?,
            receta_B = ?,
            receta_C = ?,
            receta_D = ?,
            formula_A = ?,
            formula_B = ?,
            formula_C = ?,
            formula_D = ?,
            temperatura = ?,
            meseta = ?,
            soporte = ?,
            notas = ?,
            imagenes = ?
        WHERE id = ?
        """

        valores = (
            nombre,
            datos.get("fecha", ""),
            datos["fundentes"],
            datos["delta_sio2"],
            datos["delta_al2o3"],
            json.dumps(datos["recetas"]["A"]),
            json.dumps(datos["recetas"]["B"]),
            json.dumps(datos["recetas"]["C"]),
            json.dumps(datos["recetas"]["D"]),
            json.dumps(datos["formulas"]["A"]),
            json.dumps(datos["formulas"]["B"]),
            json.dumps(datos["formulas"]["C"]),
            json.dumps(datos["formulas"]["D"]),
            datos.get("temperatura", ""),
            datos.get("meseta", ""),
            datos.get("soporte", ""),
            datos.get("comentarios", ""),
            json.dumps(datos.get("imagenes", [])),
            exp_id,
        )

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(sql, valores)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------

    def borrar_experimento(self, exp_id: int) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM currie_experimentos WHERE id = ?", (exp_id,))
        conn.commit()
        conn.close()
