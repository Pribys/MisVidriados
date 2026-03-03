"""
materias_primas_logica.py

Lógica del módulo materias_primas.
Coordina la vista con la capa de acceso a datos.
Incluye validaciones básicas y control de errores.
No contiene SQL ni código de interfaz.
"""

from typing import List, Dict, Optional, Tuple

from . import materias_primas_bd


def _validar_campos(nombre: str, analisis_oxidos: str) -> Tuple[bool, Optional[str]]:
    """
    Valida los campos obligatorios de una materia prima.
    """
    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio."
    if not analisis_oxidos or not analisis_oxidos.strip():
        return False, "El análisis de óxidos es obligatorio."
    return True, None


def listar(db_path: str) -> List[Dict]:
    """
    Devuelve el listado completo de materias primas.
    """
    return materias_primas_bd.obtener_todas(db_path)


def obtener(db_path: str, id_materia: int) -> Optional[Dict]:
    """
    Devuelve una materia prima por id.
    """
    return materias_primas_bd.obtener_por_id(db_path, id_materia)


def crear(
    db_path: str,
    nombre: str,
    analisis_oxidos: str,
    finalidad: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Crea una nueva materia prima tras validar los datos.
    """
    valido, error = _validar_campos(nombre, analisis_oxidos)
    if not valido:
        return False, error

    materias_primas_bd.insertar(db_path, nombre.strip(), analisis_oxidos.strip(), finalidad)
    return True, None


def editar(
    db_path: str,
    id_materia: int,
    nombre: str,
    analisis_oxidos: str,
    finalidad: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Edita una materia prima existente.
    """
    existente = materias_primas_bd.obtener_por_id(db_path, id_materia)
    if not existente:
        return False, "La materia prima no existe."

    valido, error = _validar_campos(nombre, analisis_oxidos)
    if not valido:
        return False, error

    materias_primas_bd.actualizar(
        db_path,
        id_materia,
        nombre.strip(),
        analisis_oxidos.strip(),
        finalidad
    )
    return True, None


def eliminar(db_path: str, id_materia: int) -> Tuple[bool, Optional[str]]:
    """
    Elimina una materia prima.
    """
    existente = materias_primas_bd.obtener_por_id(db_path, id_materia)
    if not existente:
        return False, "La materia prima no existe."

    materias_primas_bd.borrar(db_path, id_materia)
    return True, None
