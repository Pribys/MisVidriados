from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QTextEdit, QPushButton, QMessageBox,
    QListWidget, QListWidgetItem, QInputDialog
)
import sqlite3
import json

from vidriados.imagenes_vidriado_widget import ImagenesVidriadoWidget


class VidriadoEditarVista(QWidget):
    """Vista para alta y edición de vidriados.
    - Receta guardada como JSON (dict materia prima -> porcentaje)
    - Fórmula Seger guardada como JSON (dict óxido -> moles)
    - Imágenes guardadas como JSON (lista de rutas relativas)
    """

    OXIDOS = {
        "fundentes": ["Li2O", "Na2O", "K2O", "MgO", "CaO", "SrO", "BaO", "ZnO", "PbO"],
        "intermedios": ["Al2O3", "B2O3", "Fe2O3"],
        "formadores": ["SiO2", "P2O5", "TiO2", "ZrO2", "SnO2"],
    }

    def __init__(self, db_path: str, datos: dict | None, nuevo: bool = False, on_close=None):
        super().__init__()
        self.db_path = db_path
        self.datos = datos or {}
        self.nuevo = nuevo
        self.on_close = on_close
        self.campos_oxidos = {}
        self.setWindowTitle("Nuevo vidriado" if nuevo else f"Editar vidriado {self.datos.get('codigo','')}")
        self.resize(1100, 650)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)

        # ───── Columna izquierda: formulario ─────
        form = QVBoxLayout()

        fila1 = QHBoxLayout()
        self.codigo = QLineEdit(self.datos.get("codigo",""))
        self.temperatura = QLineEdit(self.datos.get("temperatura",""))
        fila1.addWidget(QLabel("Código"))
        fila1.addWidget(self.codigo, 2)
        fila1.addWidget(QLabel("Temperatura"))
        fila1.addWidget(self.temperatura, 1)
        form.addLayout(fila1)

        fila2 = QHBoxLayout()
        self.color = QLineEdit(self.datos.get("color",""))
        self.brillo = QLineEdit(self.datos.get("brillo",""))
        self.transparencia = QLineEdit(self.datos.get("transparencia",""))
        for lbl, w in (
            ("Color", self.color),
            ("Brillo", self.brillo),
            ("Transparencia", self.transparencia),
        ):
            fila2.addWidget(QLabel(lbl))
            fila2.addWidget(w)
        form.addLayout(fila2)

        form.addWidget(QLabel("Receta"))
        self.receta = QTextEdit()
        self.receta.setPlainText(self._receta_a_texto())
        self.receta.setMinimumHeight(120)
        form.addWidget(self.receta)

        form.addWidget(QLabel("Fórmula Seger"))
        form.addLayout(self._crear_grid_oxidos())

        form.addWidget(QLabel("Comentarios"))
        self.comentarios = QTextEdit()
        self.comentarios.setPlainText(self.datos.get("comentarios",""))
        self.comentarios.setMinimumHeight(80)
        form.addWidget(self.comentarios)

        botones = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")
        botones.addWidget(btn_guardar)
        botones.addWidget(btn_cancelar)
        form.addLayout(botones)

        layout.addLayout(form, 3)

        # ───── Columna central: materias primas ─────
        mp_col = QVBoxLayout()
        mp_col.addWidget(QLabel("Materias primas"))
        self.lista_mp = QListWidget()
        self.lista_mp.setMaximumWidth(220)
        mp_col.addWidget(self.lista_mp)
        layout.addLayout(mp_col, 1)

        # ───── Columna derecha: imágenes ─────
        img_col = QVBoxLayout()
        img_col.addWidget(QLabel("Imágenes del vidriado"))
        self.widget_imagenes = ImagenesVidriadoWidget("imagenes_vidriados", self)
        img_col.addWidget(self.widget_imagenes)
        layout.addLayout(img_col, 1)

        self._cargar_materias_primas()
        self._precargar_formula()
        self._precargar_imagenes()

        btn_guardar.clicked.connect(self._guardar)
        btn_cancelar.clicked.connect(self.close)
        self.lista_mp.itemDoubleClicked.connect(self._anadir_materia_prima)

    def _crear_grid_oxidos(self):
        grid = QGridLayout()
        headers = ["Fundentes", "Intermedios", "Formadores"]
        for col, h in enumerate(headers):
            grid.addWidget(QLabel(h), 0, col * 2, 1, 2)

        categorias = ["fundentes", "intermedios", "formadores"]
        max_filas = max(len(self.OXIDOS[c]) for c in categorias)

        for fila in range(max_filas):
            for col, cat in enumerate(categorias):
                lista = self.OXIDOS[cat]
                if fila < len(lista):
                    ox = lista[fila]
                    lbl = QLabel(ox)
                    campo = QLineEdit()
                    campo.setMaximumWidth(55)
                    grid.addWidget(lbl, fila + 1, col * 2)
                    grid.addWidget(campo, fila + 1, col * 2 + 1)
                    self.campos_oxidos[ox] = campo
        return grid

    def _precargar_formula(self):
        texto = self.datos.get("formula","")
        if not texto:
            return
        try:
            datos = json.loads(texto)
        except Exception:
            return
        if not isinstance(datos, dict):
            return
        for ox, val in datos.items():
            campo = self.campos_oxidos.get(ox)
            if campo:
                campo.setText(str(val))

    def _precargar_imagenes(self):
        campo = self.datos.get("imagenes")
        if not campo:
            self.widget_imagenes.set_imagenes([])
            return
        try:
            datos = json.loads(campo)
            if isinstance(datos, list):
                self.widget_imagenes.set_imagenes(datos)
            else:
                self.widget_imagenes.set_imagenes([])
        except Exception:
            self.widget_imagenes.set_imagenes([])

    def _recoger_formula(self):
        formula = {}
        for ox, campo in self.campos_oxidos.items():
            val = campo.text().strip()
            if val:
                try:
                    formula[ox] = float(val)
                except ValueError:
                    pass
        return json.dumps(formula, ensure_ascii=False)

    def _receta_a_texto(self):
        campo = self.datos.get("receta","")
        try:
            datos = json.loads(campo)
            if isinstance(datos, dict):
                return "\n".join(f"{k}: {v}" for k, v in datos.items())
        except Exception:
            pass
        return campo

    def _recoger_receta(self):
        receta = {}
        for linea in self.receta.toPlainText().splitlines():
            if ":" not in linea:
                continue
            nombre, valor = linea.split(":", 1)
            try:
                receta[nombre.strip()] = float(valor.strip())
            except ValueError:
                continue
        return json.dumps(receta, ensure_ascii=False)

    def _cargar_materias_primas(self):
        self.lista_mp.clear()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT nombre FROM materias_primas ORDER BY nombre")
            for (nombre,) in cur.fetchall():
                self.lista_mp.addItem(QListWidgetItem(nombre))

    def _anadir_materia_prima(self, item):
        nombre = item.text()
        porcentaje, ok = QInputDialog.getDouble(
            self,
            "Porcentaje",
            f"Porcentaje de {nombre}:",
            0.0,
            0.0,
            100.0,
            2
        )
        if not ok:
            return
        texto = self.receta.toPlainText().strip()
        linea = f"{nombre}: {porcentaje}"
        self.receta.setPlainText(texto + ("\n" if texto else "") + linea)

    def _guardar(self):
        try:
            formula_json = self._recoger_formula()
            receta_json = self._recoger_receta()
            imagenes_json = json.dumps(self.widget_imagenes.get_imagenes(), ensure_ascii=False)

            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                if self.nuevo:
                    cur.execute(
                        "INSERT INTO vidriados (codigo, temperatura, color, brillo, transparencia, receta, formula, imagenes, comentarios) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            self.codigo.text(),
                            self.temperatura.text(),
                            self.color.text(),
                            self.brillo.text(),
                            self.transparencia.text(),
                            receta_json,
                            formula_json,
                            imagenes_json,
                            self.comentarios.toPlainText(),
                        )
                    )
                else:
                    cur.execute(
                        "UPDATE vidriados SET codigo = ?, temperatura = ?, color = ?, brillo = ?, transparencia = ?, receta = ?, formula = ?, imagenes = ?, comentarios = ? WHERE id = ?",
                        (
                            self.codigo.text(),
                            self.temperatura.text(),
                            self.color.text(),
                            self.brillo.text(),
                            self.transparencia.text(),
                            receta_json,
                            formula_json,
                            imagenes_json,
                            self.comentarios.toPlainText(),
                            self.datos.get("id"),
                        )
                    )
                conn.commit()

            QMessageBox.information(self, "Guardado", "Vidriado guardado correctamente.")
            self.close()
            if self.on_close:
                self.on_close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
