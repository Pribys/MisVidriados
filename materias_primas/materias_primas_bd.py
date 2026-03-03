"""
materias_primas_bd.py

Capa de acceso a datos del módulo materias_primas.
Contiene exclusivamente funciones SQL para la tabla materias_primas.
No incluye lógica de negocio ni código de interfaz.
"""

import sqlite3
from typing import List, Dict, Optional


def _conectar(db_path: str) -> sqlite3.Connection:
    """
    Abre una conexión a la base de datos SQLite.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def obtener_todas(db_path: str) -> List[Dict]:
    """
    Devuelve todas las materias primas ordenadas por nombre.
    """
    conn = _conectar(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre, analisis_oxidos, finalidad
        FROM materias_primas
        ORDER BY nombre
    """)
    filas = cur.fetchall()
    conn.close()
    return [dict(fila) for fila in filas]


def obtener_por_id(db_path: str, id_materia: int) -> Optional[Dict]:
    """
    Devuelve una materia prima por su id o None si no existe.
    """
    conn = _conectar(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre, analisis_oxidos, finalidad
        FROM materias_primas
        WHERE id = ?
    """, (id_materia,))
    fila = cur.fetchone()
    conn.close()
    return dict(fila) if fila else None


def insertar(db_path: str, nombre: str, analisis_oxidos: str, finalidad: Optional[str]) -> int:
    """
    Inserta una nueva materia prima y devuelve su id.
    """
    conn = _conectar(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO materias_primas (nombre, analisis_oxidos, finalidad)
        VALUES (?, ?, ?)
    """, (nombre, analisis_oxidos, finalidad))
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return nuevo_id


def actualizar(db_path: str, id_materia: int, nombre: str, analisis_oxidos: str, finalidad: Optional[str]) -> None:
    """
    Actualiza una materia prima existente.
    """
    conn = _conectar(db_path)
    cur = conn.cursor()
    cur.execute("""
        UPDATE materias_primas
        SET nombre = ?, analisis_oxidos = ?, finalidad = ?
        WHERE id = ?
    """, (nombre, analisis_oxidos, finalidad, id_materia))
    conn.commit()
    conn.close()


def borrar(db_path: str, id_materia: int) -> None:
    """
    Elimina una materia prima por su id.
    """
    conn = _conectar(db_path)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM materias_primas
        WHERE id = ?
    """, (id_materia,))
    conn.commit()
    conn.close()
