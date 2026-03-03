
from PySide6.QtWidgets import QMessageBox


class CurrieEditor:

    def __init__(self, vista, db, widget_esquinas, widget_metadata):
        self.vista = vista
        self.db = db
        self.widget_esquinas = widget_esquinas
        self.widget_metadata = widget_metadata

        self.experimento_id = None
        self._modo_edicion = False
        self._set_modo_edicion(False)

    # ------------------------------------------------------------

    def activar_edicion(self):
        if self.experimento_id is None:
            return
        self._set_modo_edicion(True)

    def activar_guardado(self):
        self._set_modo_edicion(True)

    # ------------------------------------------------------------

    def cargar_experimento(self, exp_id: int, datos: dict):
        self.experimento_id = exp_id
        self._set_modo_edicion(False)

    # ------------------------------------------------------------

    def guardar(self):
        nombre = self.vista.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(
                self.vista,
                "Error",
                "El nombre del experimento es obligatorio."
            )
            return

        if self._modo_edicion:
            try:
                formulas, recetas = self.widget_esquinas.obtener_datos()
            except Exception as e:
                QMessageBox.warning(self.vista, "Error", str(e))
                return
        else:
            if (
                self.vista.esquinas
                and self.vista.esquinas.experimento_completo()
            ):
                formulas = {
                    k: v.copy()
                    for k, v in self.vista.esquinas.formulas.items()
                }
                recetas = {
                    k: v.copy()
                    for k, v in self.vista.esquinas.recetas.items()
                }
            else:
                try:
                    formulas, recetas = self.widget_esquinas.obtener_datos()
                except Exception as e:
                    QMessageBox.warning(self.vista, "Error", str(e))
                    return

        try:
            delta_sio2 = (
                float(self.vista.input_sio2.text())
                if self.vista.input_sio2.text()
                else 0.0
            )
            delta_al2o3 = (
                float(self.vista.input_al2o3.text())
                if self.vista.input_al2o3.text()
                else 0.0
            )
        except ValueError:
            QMessageBox.warning(
                self.vista,
                "Error",
                "ΔSiO₂ y ΔAl₂O₃ deben ser numéricos."
            )
            return

        datos = {
            "fundentes": self.vista.input_fundentes.text(),
            "fecha": self.vista.input_fecha.text(),
            "delta_sio2": delta_sio2,
            "delta_al2o3": delta_al2o3,
            "formulas": formulas,
            "recetas": recetas,
        }
        datos.update(self.widget_metadata.obtener_datos())

        if self.experimento_id is None:
            self.experimento_id = self.db.crear_experimento(nombre, datos)
        else:
            self.db.actualizar_experimento(
                self.experimento_id, nombre, datos
            )

        self.vista._cargar_experimentos()
        self._set_modo_edicion(False)

        QMessageBox.information(
            self.vista,
            "OK",
            "Experimento guardado correctamente."
        )

    # ------------------------------------------------------------

    def borrar(self):
        if self.experimento_id is None:
            return

        resp = QMessageBox.question(
            self.vista,
            "Confirmar",
            "¿Seguro que quieres borrar este experimento?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        self.db.borrar_experimento(self.experimento_id)
        self.experimento_id = None
        self.vista.input_nombre.clear()
        self.vista._cargar_experimentos()
        self._set_modo_edicion(False)

        QMessageBox.information(
            self.vista,
            "OK",
            "Experimento borrado."
        )

    # ------------------------------------------------------------

    def _set_modo_edicion(self, activo: bool):
        self._modo_edicion = activo
        editable_iniciales = activo or self.experimento_id is None

        for w in (
            self.vista.input_nombre,
            self.vista.input_fecha,
            self.vista.input_fundentes,
            self.vista.input_sio2,
            self.vista.input_al2o3,
        ):
            w.setReadOnly(not editable_iniciales)

        self.widget_metadata.set_modo_edicion(activo)
        self.widget_esquinas.set_modo_edicion(activo)

        self.vista.btn_guardar.setEnabled(activo)
        self.vista.btn_principal.setEnabled(editable_iniciales)
        self.vista.btn_editar.setEnabled(
            not activo and self.experimento_id is not None
        )
