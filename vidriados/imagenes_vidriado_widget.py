from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QFileDialog, QMessageBox
)
import os
import shutil


class ImagenesVidriadoWidget(QWidget):
    """Widget autocontenido para la gestión de imágenes de un vidriado.

    - Muestra una lista de imágenes asociadas (solo nombre de archivo).
    - Permite añadir imágenes copiándolas a la carpeta imagenes_vidriados.
    - Permite eliminar imágenes de la lista.
    - No guarda nada en BD: solo gestiona nombres de archivo.
    """

    def __init__(self, carpeta_imagenes: str, parent=None):
        super().__init__(parent)
        self.carpeta_imagenes = carpeta_imagenes
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        botones = QHBoxLayout()
        btn_add = QPushButton("Añadir imagen")
        btn_del = QPushButton("Eliminar imagen")
        botones.addWidget(btn_add)
        botones.addWidget(btn_del)
        botones.addStretch()

        layout.addLayout(botones)

        btn_add.clicked.connect(self._anadir_imagenes)
        btn_del.clicked.connect(self._eliminar_imagen)

    # ───── API pública ─────

    def set_imagenes(self, rutas):
        self.lista.clear()
        for r in rutas or []:
            self.lista.addItem(r)

    def get_imagenes(self):
        return [
            self.lista.item(i).text()
            for i in range(self.lista.count())
        ]

    # ───── Lógica interna ─────

    def _anadir_imagenes(self):
        archivos, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar imágenes",
            "",
            "Imágenes (*.jpg *.jpeg *.png *.webp)"
        )
        if not archivos:
            return

        for origen in archivos:
            try:
                nombre = os.path.basename(origen)
                destino = os.path.join(self.carpeta_imagenes, nombre)

                if not os.path.exists(self.carpeta_imagenes):
                    os.makedirs(self.carpeta_imagenes)

                shutil.copy2(origen, destino)

                # Solo guardamos el nombre del archivo
                ruta_rel = nombre

                if ruta_rel not in self.get_imagenes():
                    self.lista.addItem(ruta_rel)

            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"No se pudo añadir la imagen:\n{e}"
                )

    def _eliminar_imagen(self):
        fila = self.lista.currentRow()
        if fila >= 0:
            self.lista.takeItem(fila)
