# -----------------------------------------------------------------------------
# 06_stull_vista.py
#
# Vista principal del módulo Stull.
#
# Características:
# - Filtros químicos activos en tiempo real
# - Ventana Stull reactiva (actualización automática)
# - Gestión de múltiples experimentos Currie
# - Lista de experimentos activos (doble clic elimina)
# - Modo "Stull" (BD + Currie)
# - Modo "Currie" (solo puntos Currie)
#
# Encapsulado. No modifica otros módulos.
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QGroupBox, QGridLayout,
    QComboBox, QCheckBox
)

from range_slider import RangeSlider
from stull.stull_controlador import StullControlador
from stull.stull_plot import StullPlot


class StullVista(QWidget):

    FUNDENTES_BAJA = ["Li2O", "K2O", "Na2O", "PbO", "B2O3"]
    FUNDENTES_ALTA = ["MgO", "CaO", "SrO", "BaO", "ZnO"]

    def __init__(self, db_path: str):
        super().__init__()
        self.controlador = StullControlador(db_path)

        self._vidriados_bd = []
        self._experimentos_currie_activos = {}
        self._checks_fundentes = {}
        self._stull_window = None
        self._modo_currie_solo = False

        self._init_ui()
        self._cargar_datos()

    # ------------------------------------------------------------------

    def _init_ui(self):
        layout = QHBoxLayout(self)

        # Columna izquierda
        col_izq = QVBoxLayout()

        fila_botones = QHBoxLayout()
        self.btn_stull = QPushButton("Stull")
        self.btn_currie = QPushButton("Currie")
        fila_botones.addWidget(self.btn_stull)
        fila_botones.addWidget(self.btn_currie)

        col_izq.addLayout(fila_botones)

        self.lista = QListWidget()
        col_izq.addWidget(self.lista)

        layout.addLayout(col_izq, 1)

        # Columna derecha (filtros)
        filtros_box = QGroupBox("Filtros")
        col_der = QVBoxLayout(filtros_box)

        # Código
        cod_box = QGroupBox("Código")
        cod_lay = QHBoxLayout(cod_box)
        cod_lay.addWidget(QLabel("Empieza por:"))
        self.codigo_edit = QLineEdit()
        cod_lay.addWidget(self.codigo_edit)
        col_der.addWidget(cod_box)

        # Temperatura
        temp_box = QGroupBox("Temperatura (°C)")
        temp_lay = QVBoxLayout(temp_box)
        self.temp_slider = RangeSlider(800, 1300, 800, 1300, precision=0)
        temp_lay.addWidget(self.temp_slider)
        col_der.addWidget(temp_box)

        # Composición
        chem_box = QGroupBox("Composición (moles)")
        chem_lay = QVBoxLayout(chem_box)

        fila_sio2 = QHBoxLayout()
        fila_sio2.addWidget(QLabel("SiO₂"))
        self.si_slider = RangeSlider(0.0, 8.0, 0.0, 8.0, precision=2)
        fila_sio2.addWidget(self.si_slider)
        chem_lay.addLayout(fila_sio2)

        fila_al2o3 = QHBoxLayout()
        fila_al2o3.addWidget(QLabel("Al₂O₃"))
        self.al_slider = RangeSlider(0.0, 2.0, 0.0, 2.0, precision=2)
        fila_al2o3.addWidget(self.al_slider)
        chem_lay.addLayout(fila_al2o3)

        col_der.addWidget(chem_box)

        # Fundentes
        fund_box = QGroupBox("Fundentes (≥ 0.1 moles)")
        fund_lay = QGridLayout(fund_box)

        for col, ox in enumerate(self.FUNDENTES_BAJA):
            chk = QCheckBox(ox)
            self._checks_fundentes[ox] = chk
            fund_lay.addWidget(chk, 0, col)

        for col, ox in enumerate(self.FUNDENTES_ALTA):
            chk = QCheckBox(ox)
            self._checks_fundentes[ox] = chk
            fund_lay.addWidget(chk, 1, col)

        col_der.addWidget(fund_box)

        # Currie
        currie_box = QGroupBox("Experimento Currie")
        currie_lay = QVBoxLayout(currie_box)

        self.combo_currie = QComboBox()
        currie_lay.addWidget(self.combo_currie)

        self.lista_currie_activos = QListWidget()
        currie_lay.addWidget(self.lista_currie_activos)

        col_der.addWidget(currie_box)

        col_der.addStretch()
        layout.addWidget(filtros_box, 3)

        # Conexiones
        self.btn_stull.clicked.connect(self._modo_todo)
        self.btn_currie.clicked.connect(self._modo_currie)

        self.codigo_edit.textChanged.connect(self._aplicar_filtros)
        self.temp_slider.rangeChanged.connect(self._aplicar_filtros)
        self.si_slider.rangeChanged.connect(self._aplicar_filtros)
        self.al_slider.rangeChanged.connect(self._aplicar_filtros)

        self.combo_currie.currentIndexChanged.connect(self._agregar_currie)
        self.lista_currie_activos.itemDoubleClicked.connect(self._eliminar_currie)

        for chk in self._checks_fundentes.values():
            chk.stateChanged.connect(self._aplicar_filtros)

    # ------------------------------------------------------------------

    def _modo_todo(self):
        self._modo_currie_solo = False
        self._mostrar_stull()

    def _modo_currie(self):
        self._modo_currie_solo = True
        self._mostrar_stull()

    # ------------------------------------------------------------------

    def _cargar_datos(self):
        self._vidriados_bd = self.controlador.obtener_vidriados()

        self.combo_currie.clear()
        self.combo_currie.addItem("— añadir experimento —", None)

        for exp in self.controlador.obtener_experimentos_currie():
            self.combo_currie.addItem(exp["nombre"], exp["id"])

        self._aplicar_filtros()

    # ------------------------------------------------------------------

    def _agregar_currie(self):
        exp_id = self.combo_currie.currentData()
        if not exp_id or exp_id in self._experimentos_currie_activos:
            return

        nombre = self.combo_currie.currentText()
        puntos = self.controlador.generar_currie(exp_id)

        self._experimentos_currie_activos[exp_id] = {
            "nombre": nombre,
            "puntos": puntos
        }

        self.lista_currie_activos.addItem(nombre)
        self._aplicar_filtros()

    # ------------------------------------------------------------------

    def _eliminar_currie(self, item):
        nombre = item.text()

        for exp_id, datos in list(self._experimentos_currie_activos.items()):
            if datos["nombre"] == nombre:
                del self._experimentos_currie_activos[exp_id]
                break

        self.lista_currie_activos.takeItem(
            self.lista_currie_activos.row(item)
        )

        self._aplicar_filtros()

    # ------------------------------------------------------------------

    def _aplicar_filtros(self):
        codigo_pref = self.codigo_edit.text().strip().upper()
        tmin, tmax = self.temp_slider.lower, self.temp_slider.upper
        simin, simax = self.si_slider.lower, self.si_slider.upper
        almin, almax = self.al_slider.lower, self.al_slider.upper

        fundentes_activos = [
            ox for ox, chk in self._checks_fundentes.items()
            if chk.isChecked()
        ]

        currie_puntos = []
        for datos in self._experimentos_currie_activos.values():
            currie_puntos.extend(datos["puntos"])

        datos_totales = self._vidriados_bd + currie_puntos
        filtrados = []

        for vid in datos_totales:

            if self._modo_currie_solo and vid.get("tipo") != "currie":
                continue

            codigo = (vid.get("codigo") or "").upper()
            if codigo_pref and not codigo.startswith(codigo_pref):
                continue

            try:
                temp = float(vid.get("temperatura") or 0)
            except Exception:
                continue

            if temp < tmin or temp > tmax:
                continue

            si = vid.get("sio2", 0.0)
            al = vid.get("al2o3", 0.0)

            if si < simin or si > simax:
                continue
            if al < almin or al > almax:
                continue

            formula = vid.get("formula", {})

            for ox in fundentes_activos:
                if formula.get(ox, 0.0) < 0.1:
                    break
            else:
                filtrados.append(vid)

        self.lista.clear()
        for vid in filtrados:
            item = QListWidgetItem(vid.get("codigo", ""))
            item.setData(1, vid)
            self.lista.addItem(item)

        if self._stull_window:
            self._stull_window.actualizar_puntos(filtrados)

    # ------------------------------------------------------------------

    def _mostrar_stull(self):
        puntos = []
        for i in range(self.lista.count()):
            vid = self.lista.item(i).data(1)
            puntos.append(vid)

        if not self._stull_window:
            self._stull_window = StullPlot(puntos, self)
            self._stull_window.show()
        else:
            self._stull_window.actualizar_puntos(puntos)
            self._stull_window.show()
