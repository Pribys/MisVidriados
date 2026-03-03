
import sqlite3

class VidriadosModelo:
    """Acceso a datos de la tabla vidriados."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def obtener_lista(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, codigo FROM vidriados ORDER BY codigo")
            return cur.fetchall()

    def obtener_por_id(self, vidriado_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM vidriados WHERE id = ?", (vidriado_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def obtener_lista_filtrable(self):
        """Devuelve todos los campos filtrables de los vidriados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT
                    id,
                    codigo,
                    temperatura,
                    color,
                    brillo,
                    transparencia,
                    receta,
                    formula
                FROM vidriados
                ORDER BY codigo
                """
            )
            return [dict(row) for row in cur.fetchall()]
