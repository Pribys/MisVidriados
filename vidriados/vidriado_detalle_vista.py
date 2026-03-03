from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QGroupBox, QPushButton, QMessageBox, QScrollArea
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sqlite3
import os
import json
import re
import sys

_SUBS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

class VidriadoDetalleVista(QWidget):
    """Vista de detalle de un vidriado.
    Muestra receta, fórmula Seger, comentarios y galería de imágenes.
    Fórmula y receta se leen exclusivamente como JSON.
    """

    def __init__(self, db_path: str, datos: dict, on_delete=None):
        super().__init__()
        self.db_path = db_path
        self.datos = datos
        self.on_delete = on_delete
        self.setWindowTitle(f"Vidriado {datos.get('codigo','')}")
        self.resize(950, 700)
        self._init_ui()

    def _init_ui(self):
        main = QVBoxLayout(self)

        sup_box = QGroupBox("Imagen y datos")
        sup_lay = QHBoxLayout(sup_box)

        galeria = QScrollArea()
        galeria.setWidgetResizable(True)
        galeria.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        galeria.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        cont_img = QWidget()
        lay_img = QHBoxLayout(cont_img)
        lay_img.setContentsMargins(0, 0, 0, 0)
        lay_img.setSpacing(8)

        for ruta in self._rutas_imagenes():
            lbl = QLabel()
            lbl.setFixedSize(200, 200)
            lbl.setAlignment(Qt.AlignCenter)
            if os.path.exists(ruta):
                lbl.setPixmap(QPixmap(ruta).scaled(
                    200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                lbl.setText("Imagen no encontrada")
            lay_img.addWidget(lbl)

        lay_img.addStretch()
        galeria.setWidget(cont_img)
        sup_lay.addWidget(galeria, 2)

        datos_lay = QVBoxLayout()
        datos_lay.addWidget(QLabel(f"Color: {self.datos.get('color','')}"))
        datos_lay.addWidget(QLabel(f"Brillo: {self.datos.get('brillo','')}"))
        datos_lay.addWidget(QLabel(f"Transparencia: {self.datos.get('transparencia','')}"))
        datos_lay.addWidget(QLabel(f"Temperatura: {self.datos.get('temperatura','')}"))
        datos_lay.addSpacing(10)

        btn_editar = QPushButton("Editar")
        btn_borrar = QPushButton("Borrar")
        btn_borrar.setStyleSheet("color: darkred;")

        datos_lay.addWidget(btn_editar)
        datos_lay.addWidget(btn_borrar)
        datos_lay.addStretch()

        btn_editar.clicked.connect(self._editar)
        btn_borrar.clicked.connect(self._borrar)

        sup_lay.addLayout(datos_lay, 1)
        main.addWidget(sup_box)

        mid = QHBoxLayout()

        rec_box = QGroupBox("Receta")
        rec_lay = QVBoxLayout(rec_box)
        txt_rec = QTextEdit()
        txt_rec.setReadOnly(True)
        txt_rec.setPlainText(self._texto_receta())
        rec_lay.addWidget(txt_rec)
        mid.addWidget(rec_box, 1)

        for_box = QGroupBox("Fórmula Seger")
        for_lay = QGridLayout(for_box)

        for_lay.addWidget(QLabel("Fundentes"), 0, 0)
        for_lay.addWidget(QLabel("Intermedios"), 0, 1)
        for_lay.addWidget(QLabel("Formadores"), 0, 2)

        fund, inter, form, ratio = self._formula_columnas()
        filas = max(len(fund), len(inter), len(form))
        for i in range(filas):
            for_lay.addWidget(QLabel(fund[i] if i < len(fund) else ""), i+1, 0)
            for_lay.addWidget(QLabel(inter[i] if i < len(inter) else ""), i+1, 1)
            for_lay.addWidget(QLabel(form[i] if i < len(form) else ""), i+1, 2)

        if ratio is not None:
            fila_ratio = filas + 1
            for_lay.addWidget(QLabel(f"SiO₂ / Al₂O₃  {ratio:.2f}"), fila_ratio, 1)

        mid.addWidget(for_box, 1)
        main.addLayout(mid)

        com_box = QGroupBox("Comentarios")
        com_lay = QVBoxLayout(com_box)
        txt_com = QTextEdit()
        txt_com.setReadOnly(True)
        txt_com.setPlainText(self.datos.get("comentarios",""))
        com_lay.addWidget(txt_com)
        main.addWidget(com_box)

    def _editar(self):
        from vidriados.vidriado_editar_vista import VidriadoEditarVista
        self.editor = VidriadoEditarVista(
            self.db_path,
            self.datos,
            nuevo=False,
            on_close=self._cerrar_y_refrescar
        )
        self.editor.show()

    def _cerrar_y_refrescar(self):
        if self.on_delete:
            self.on_delete()
        self.close()

    def _borrar(self):
        resp = QMessageBox.question(
            self,
            "Confirmar borrado",
            "¿Seguro que quieres borrar este vidriado?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM vidriados WHERE id = ?", (self.datos["id"],))
                conn.commit()
            if self.on_delete:
                self.on_delete()
            self.close()

    def _rutas_imagenes(self):
        campo = self.datos.get("imagenes")
        if not campo:
            return []
        try:
            datos = json.loads(campo)
            if isinstance(datos, list):
                base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
                carpeta = os.path.join(base_path, "datos_usuario", "imagenes_vidriados")
                return [
                    os.path.join(carpeta, r)
                    for r in datos
                ]
        except Exception:
            pass
        return []
        try:
            datos = json.loads(campo)
            if isinstance(datos, list):
                return [
                    os.path.join("imagenes_vidriados", r).replace("\\", os.sep)
                    for r in datos
                ]
        except Exception:
            pass
        return []

    def _texto_receta(self):
        campo = self.datos.get("receta","")
        try:
            datos = json.loads(campo)
            if isinstance(datos, dict):
                return "\n".join(f"{k}: {v}" for k, v in datos.items())
        except Exception:
            pass
        return campo

    def _formula_columnas(self):
        texto = self.datos.get("formula","")
        try:
            datos = json.loads(texto)
        except Exception:
            return [], [], [], None

        if not isinstance(datos, dict):
            return [], [], [], None

        fund, inter, form = [], [], []

        si = datos.get("SiO2")
        al = datos.get("Al2O3")
        ratio = None
        if isinstance(si, (int, float)) and isinstance(al, (int, float)) and al != 0:
            ratio = si / al

        for ox, val in datos.items():
            ox_fmt = self._subindices(ox)
            item = f"{ox_fmt}  {val}"

            if ox in ("Al2O3", "B2O3", "Fe2O3"):
                inter.append(item)
            elif ox.endswith("O2"):
                form.append(item)
            else:
                fund.append(item)

        return fund, inter, form, ratio

    def _subindices(self, oxido):
        return re.sub(r"\d", lambda m: m.group().translate(_SUBS), oxido)
