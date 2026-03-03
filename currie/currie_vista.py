
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox
)

from currie.currie_esquinas import CurrieEsquinas
from currie.currie_seger_dialog import CurrieSegerDialog
from currie.currie_db import CurrieDB
from currie.currie_recetas import CurrieRecetas
from currie.currie_widget_esquinas import CurrieWidgetEsquinas
from currie.currie_widget_metadata import CurrieWidgetMetadata
from currie.currie_editor import CurrieEditor


class CurrieVista(QWidget):

    def __init__(self, db_path: str):
        super().__init__()
        self.db = CurrieDB(db_path)

        self.esquinas = None
        self.formula_fundentes = None
        self.dialogo_seger = None
        self.calculador_recetas = None

        self._construir_ui()
        self.editor = CurrieEditor(
            vista=self,
            db=self.db,
            widget_esquinas=self.widget_esquinas,
            widget_metadata=self.widget_metadata,
        )

        self._conectar()
        self._cargar_experimentos()

    # ------------------------------------------------------------

    def _construir_ui(self):
        layout_principal = QHBoxLayout(self)

        col_izq = QVBoxLayout()
        zona_superior = QHBoxLayout()

        datos = QVBoxLayout()
        datos.addWidget(QLabel("Datos iniciales del experimento"))

        f0 = QHBoxLayout()
        f0.addWidget(QLabel("Nombre:"))
        self.input_nombre = QLineEdit()
        f0.addWidget(self.input_nombre)
        datos.addLayout(f0)

        f_fecha = QHBoxLayout()
        f_fecha.addWidget(QLabel("Fecha:"))
        self.input_fecha = QLineEdit()
        f_fecha.addWidget(self.input_fecha)
        datos.addLayout(f_fecha)

        f1 = QHBoxLayout()
        f1.addWidget(QLabel("Columna fundente (UMF):"))
        self.input_fundentes = QLineEdit()
        f1.addWidget(self.input_fundentes)
        datos.addLayout(f1)

        f2 = QHBoxLayout()
        f2.addWidget(QLabel("Δ SiO₂:"))
        self.input_sio2 = QLineEdit()
        f2.addWidget(self.input_sio2)
        f2.addWidget(QLabel("Δ Al₂O₃:"))
        self.input_al2o3 = QLineEdit()
        f2.addWidget(self.input_al2o3)
        datos.addLayout(f2)

        self.btn_principal = QPushButton("Calcular C")
        datos.addWidget(self.btn_principal)

        f_crud = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar experimento")
        self.btn_editar = QPushButton("Editar experimento")
        self.btn_borrar = QPushButton("Borrar experimento")

        f_crud.addWidget(self.btn_guardar)
        f_crud.addWidget(self.btn_editar)
        f_crud.addWidget(self.btn_borrar)
        datos.addLayout(f_crud)

        receta_ind = QVBoxLayout()
        receta_ind.addWidget(QLabel("Receta del vidriado"))

        f3 = QHBoxLayout()
        f3.addWidget(QLabel("Nº (1–35):"))
        self.input_num_vidriado = QLineEdit()
        self.input_num_vidriado.setMaximumWidth(60)
        f3.addWidget(self.input_num_vidriado)
        receta_ind.addLayout(f3)

        from PySide6.QtWidgets import QTextEdit
        self.texto_receta_individual = QTextEdit()
        self.texto_receta_individual.setReadOnly(True)
        receta_ind.addWidget(self.texto_receta_individual)

        zona_superior.addLayout(datos, 2)
        zona_superior.addLayout(receta_ind, 1)

        self.widget_esquinas = CurrieWidgetEsquinas()
        col_izq.addLayout(zona_superior, 1)
        col_izq.addWidget(self.widget_esquinas, 2)

        col_der = QVBoxLayout()
        col_der.addWidget(QLabel("Experimentos Currie guardados"))

        self.combo_experimentos = QComboBox()
        col_der.addWidget(self.combo_experimentos)

        self.widget_metadata = CurrieWidgetMetadata()
        col_der.addWidget(self.widget_metadata, 1)

        layout_principal.addLayout(col_izq, 3)
        layout_principal.addLayout(col_der, 1)

    # ------------------------------------------------------------

    def _conectar(self):
        self.btn_principal.clicked.connect(self._accion_principal)
        self.btn_guardar.clicked.connect(self.editor.guardar)
        self.btn_editar.clicked.connect(self.editor.activar_edicion)
        self.btn_borrar.clicked.connect(self.editor.borrar)
        self.combo_experimentos.currentIndexChanged.connect(self._importar_experimento)
        self.input_num_vidriado.returnPressed.connect(self._calcular_vidriado_individual)

    # ------------------------------------------------------------

    def _cargar_experimentos(self):
        self.combo_experimentos.blockSignals(True)
        self.combo_experimentos.clear()
        self.combo_experimentos.addItem("-- Seleccionar experimento --", None)
        for exp_id, nombre in self.db.listar_experimentos():
            self.combo_experimentos.addItem(nombre, exp_id)
        self.combo_experimentos.blockSignals(False)

    # ------------------------------------------------------------

    def _importar_experimento(self):
        exp_id = self.combo_experimentos.currentData()
        if exp_id is None:
            return

        datos = self.db.cargar_experimento(exp_id)
        if not datos:
            return

        self.input_nombre.setText(self.combo_experimentos.currentText())
        self.input_fecha.setText(datos.get("fecha", ""))
        self.input_fundentes.setText(datos["fundentes"])
        self.input_sio2.setText(str(datos["delta_sio2"]))
        self.input_al2o3.setText(str(datos["delta_al2o3"]))

        self.esquinas = CurrieEsquinas(datos["delta_sio2"], datos["delta_al2o3"])
        self.esquinas.formulas.update(datos["formulas"])
        self.esquinas.recetas.update(datos["recetas"])
        self.esquinas._estado = None

        self.calculador_recetas = CurrieRecetas(self.esquinas.recetas)
        self.widget_esquinas.actualizar(self.esquinas.formulas, self.esquinas.recetas)
        self.widget_metadata.cargar_datos(datos)

        self.editor.cargar_experimento(exp_id, datos)

    # ------------------------------------------------------------

    def _accion_principal(self):
        if not self.esquinas:
            self._iniciar_experimento()
        else:
            self._abrir_seger()

    def _iniciar_experimento(self):
        try:
            delta_sio2 = float(self.input_sio2.text())
            delta_al2o3 = float(self.input_al2o3.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "ΔSiO₂ y ΔAl₂O₃ deben ser numéricos.")
            return

        self.formula_fundentes = self._parsear_fundentes(self.input_fundentes.text())
        if not self.formula_fundentes:
            QMessageBox.warning(self, "Error", "Columna fundente inválida.")
            return

        self.esquinas = CurrieEsquinas(delta_sio2, delta_al2o3)
        self.editor.experimento_id = None
        self._abrir_seger()

    # ------------------------------------------------------------

    def _abrir_seger(self):
        formula_obj = self.esquinas.get_formula_objetivo() or self.formula_fundentes
        self.dialogo_seger = CurrieSegerDialog(
            db_path=self.db.db_path,
            formula_inicial=formula_obj,
            on_resultado=self._recibir_resultado
        )
        self.dialogo_seger.exec()

    def _recibir_resultado(self, formula: dict, receta: dict):
        self.esquinas.registrar_resultado(formula, receta)

        if self.esquinas._estado is None:
            self.calculador_recetas = CurrieRecetas(self.esquinas.recetas)
            self.editor.activar_guardado()

        self.widget_esquinas.actualizar(self.esquinas.formulas, self.esquinas.recetas)

    # ------------------------------------------------------------

    def _calcular_vidriado_individual(self):
        if not self.calculador_recetas:
            return
        try:
            n = int(self.input_num_vidriado.text())
        except ValueError:
            return

        receta = self.calculador_recetas.calcular(n)
        texto = []
        for mp, val in sorted(receta.items()):
            texto.append(f"{mp}: {val:.2f} %")
        self.texto_receta_individual.setPlainText("\n".join(texto))

    # ------------------------------------------------------------

    @staticmethod
    def _parsear_fundentes(texto: str):
        if not texto.strip():
            return None
        f = {}
        for parte in texto.split(","):
            if "=" not in parte:
                return None
            ox, val = parte.split("=", 1)
            try:
                f[ox.strip()] = float(val.strip())
            except ValueError:
                return None
        return f
