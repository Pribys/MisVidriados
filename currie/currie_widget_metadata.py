
"""
Widget de metadatos del experimento Currie (columna derecha).

Responsabilidad:
- Mostrar y editar metadatos del experimento.
- Mostrar miniaturas de imágenes asociadas.
- Permitir añadir y eliminar imágenes (solo gestión de lista).
- NO guarda en base de datos.
"""

import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit,
    QListWidget, QListWidgetItem, QDialog,
    QScrollArea, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Qt


class VisorImagen(QDialog):
    """Ventana para mostrar una imagen a tamaño completo."""

    def __init__(self, ruta_imagen: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(ruta_imagen))

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(ruta_imagen)
        label.setPixmap(pixmap)

        scroll.setWidget(label)
        layout.addWidget(scroll)

        self.resize(700, 1000)


class CurrieWidgetMetadata(QWidget):

    ICON_SIZE = QSize(128, 128)

    def __init__(self, parent=None, imagenes_dir="imagenes_currie"):
        super().__init__(parent)

        app_root = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.imagenes_dir = os.path.join(
            app_root,
            "datos_usuario",
            imagenes_dir
        )

        self._construir_ui()
        self.set_modo_edicion(False)

    # ------------------------------------------------------------

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        fila_temp = QHBoxLayout()
        fila_temp.addWidget(QLabel("Temperatura:"))
        self.input_temperatura = QLineEdit()
        self.input_temperatura.setMaximumWidth(80)
        fila_temp.addWidget(self.input_temperatura)

        fila_temp.addWidget(QLabel("Meseta:"))
        self.input_meseta = QLineEdit()
        self.input_meseta.setMaximumWidth(80)
        fila_temp.addWidget(self.input_meseta)
        layout.addLayout(fila_temp)

        fila_soporte = QHBoxLayout()
        fila_soporte.addWidget(QLabel("Soporte:"))
        self.input_soporte = QLineEdit()
        fila_soporte.addWidget(self.input_soporte)
        layout.addLayout(fila_soporte)

        layout.addWidget(QLabel("Comentarios"))
        self.texto_comentarios = QTextEdit()
        layout.addWidget(self.texto_comentarios, 1)

        layout.addWidget(QLabel("Imágenes"))

        fila_img_btn = QHBoxLayout()
        self.btn_add_img = QPushButton("Añadir imagen")
        self.btn_del_img = QPushButton("Borrar imagen")
        fila_img_btn.addWidget(self.btn_add_img)
        fila_img_btn.addWidget(self.btn_del_img)
        layout.addLayout(fila_img_btn)

        self.lista_imagenes = QListWidget()
        self.lista_imagenes.setViewMode(QListWidget.IconMode)
        self.lista_imagenes.setIconSize(self.ICON_SIZE)
        self.lista_imagenes.setResizeMode(QListWidget.Adjust)
        self.lista_imagenes.setMovement(QListWidget.Static)
        self.lista_imagenes.setUniformItemSizes(True)
        self.lista_imagenes.itemDoubleClicked.connect(self._abrir_imagen)
        layout.addWidget(self.lista_imagenes, 1)

        self.btn_add_img.clicked.connect(self._añadir_imagen_dialogo)
        self.btn_del_img.clicked.connect(self._borrar_imagen_seleccionada)

    # ------------------------------------------------------------

    def set_modo_edicion(self, activo: bool):
        self.input_temperatura.setReadOnly(not activo)
        self.input_meseta.setReadOnly(not activo)
        self.input_soporte.setReadOnly(not activo)
        self.texto_comentarios.setReadOnly(not activo)

        self.btn_add_img.setEnabled(activo)
        self.btn_del_img.setEnabled(activo)

        self.lista_imagenes.setEnabled(True)

    # ------------------------------------------------------------

    def cargar_datos(self, datos: dict):
        self.input_temperatura.setText(str(datos.get("temperatura", "")))
        self.input_meseta.setText(str(datos.get("meseta", "")))
        self.input_soporte.setText(datos.get("soporte", ""))
        self.texto_comentarios.setPlainText(datos.get("comentarios", ""))

        self.lista_imagenes.clear()
        for valor in datos.get("imagenes", []):
            self._añadir_item_imagen(valor)

    # ------------------------------------------------------------

    def _resolver_ruta(self, valor: str) -> str:
        valor = valor.replace("\\", "/")
        if "imagenes_currie/" in valor:
            return os.path.join(
                os.path.dirname(self.imagenes_dir),
                valor
            )
        return os.path.join(self.imagenes_dir, valor)

    def _añadir_item_imagen(self, valor: str):
        ruta = self._resolver_ruta(valor)
        item = QListWidgetItem()
        item.setSizeHint(self.ICON_SIZE)
        item.setData(Qt.UserRole, ruta)

        if os.path.isfile(ruta):
            pixmap = QPixmap(ruta)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    self.ICON_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                item.setIcon(QIcon(pixmap))

        item.setText("")
        self.lista_imagenes.addItem(item)

    # ------------------------------------------------------------

    def _añadir_imagen_dialogo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not ruta:
            return

        nombre = os.path.basename(ruta)
        destino = os.path.join(self.imagenes_dir, nombre)

        if not os.path.isdir(self.imagenes_dir):
            os.makedirs(self.imagenes_dir, exist_ok=True)

        if not os.path.isfile(destino):
            try:
                with open(ruta, "rb") as fsrc, open(destino, "wb") as fdst:
                    fdst.write(fsrc.read())
            except OSError:
                QMessageBox.warning(self, "Error", "No se pudo copiar la imagen.")
                return

        self._añadir_item_imagen(nombre)

    # ------------------------------------------------------------

    def _borrar_imagen_seleccionada(self):
        item = self.lista_imagenes.currentItem()
        if not item:
            return

        resp = QMessageBox.question(
            self,
            "Confirmar",
            "¿Quitar esta imagen del experimento?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        fila = self.lista_imagenes.row(item)
        self.lista_imagenes.takeItem(fila)

    # ------------------------------------------------------------

    def _abrir_imagen(self, item: QListWidgetItem):
        ruta = item.data(Qt.UserRole)
        if ruta and os.path.isfile(ruta):
            visor = VisorImagen(ruta, self)
            visor.setModal(False)
            visor.show()

    # ------------------------------------------------------------

    def obtener_datos(self) -> dict:
        return {
            "temperatura": self.input_temperatura.text(),
            "meseta": self.input_meseta.text(),
            "soporte": self.input_soporte.text(),
            "comentarios": self.texto_comentarios.toPlainText(),
            "imagenes": [
                os.path.basename(
                    self.lista_imagenes.item(i).data(Qt.UserRole)
                )
                for i in range(self.lista_imagenes.count())
            ],
        }
