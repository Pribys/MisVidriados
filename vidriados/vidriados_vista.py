from PySide6.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QGroupBox, QCheckBox, QGridLayout, QComboBox
)
from vidriados.vidriados_controlador import VidriadosControlador
from range_slider import RangeSlider
import json


class VidriadosVista(QWidget):
    """Vista principal del módulo vidriados.

    Filtros incluidos:
    - Código (prefijo incremental)
    - Temperatura (RangeSlider, enteros)
    - Composición (sliders decimales)
    - Fundentes (presencia >= 0.1 moles)
    - Aspecto visual (color, transparencia, brillo)
    """

    FUNDENTES_BAJA = ["Li2O", "K2O", "Na2O", "PbO", "B2O3"]
    FUNDENTES_ALTA = ["MgO", "CaO", "SrO", "BaO", "ZnO"]

    def __init__(self, db_path: str):
        super().__init__()
        self.controlador = VidriadosControlador(db_path)
        self._vidriados = []
        self._checks_fundentes = {}
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)

        # ───── Columna izquierda ─────
        col_izq = QVBoxLayout()

        self.btn_nuevo = QPushButton("Nuevo vidriado")
        col_izq.addWidget(self.btn_nuevo)

        self.lista = QListWidget()
        col_izq.addWidget(self.lista)

        fila_contador = QHBoxLayout()
        fila_contador.addWidget(QLabel("Vidriados mostrados:"))
        self.contador = QLineEdit()
        self.contador.setReadOnly(True)
        self.contador.setMaximumWidth(60)
        fila_contador.addWidget(self.contador)
        fila_contador.addStretch()
        col_izq.addLayout(fila_contador)

        layout.addLayout(col_izq, 1)

        # ───── Columna derecha: filtros ─────
        filtros_box = QGroupBox("Filtros")
        col_der = QVBoxLayout(filtros_box)

        # Código
        cod_box = QGroupBox("Código")
        cod_lay = QHBoxLayout(cod_box)
        cod_lay.addWidget(QLabel("Empieza por:"))
        self.codigo_edit = QLineEdit()
        self.codigo_edit.setPlaceholderText("CN, CN0, CN01…")
        cod_lay.addWidget(self.codigo_edit)
        col_der.addWidget(cod_box)

        # Temperatura
        temp_box = QGroupBox("Temperatura (°C)")
        temp_lay = QVBoxLayout(temp_box)
        self.temp_slider = RangeSlider(800, 1300, 810, 1290, precision=0)
        temp_lay.addWidget(self.temp_slider)
        col_der.addWidget(temp_box)

        # Composición
        chem_box = QGroupBox("Composición (moles)")
        chem_lay = QVBoxLayout(chem_box)

        fila_sio2 = QHBoxLayout()
        fila_sio2.addWidget(QLabel("SiO₂"))
        self.si_slider = RangeSlider(0.5, 8.0, 0.8, 8.0, precision=2)
        fila_sio2.addWidget(self.si_slider)
        chem_lay.addLayout(fila_sio2)

        fila_al2o3 = QHBoxLayout()
        fila_al2o3.addWidget(QLabel("Al₂O₃"))
        self.al_slider = RangeSlider(0.0, 2.0, 0.1, 2.0, precision=2)
        fila_al2o3.addWidget(self.al_slider)
        chem_lay.addLayout(fila_al2o3)

        fila_ratio = QHBoxLayout()
        fila_ratio.addWidget(QLabel("SiO₂ / Al₂O₃"))
        self.ratio_slider = RangeSlider(1.0, 25.0, 1.5, 25.0, precision=2)
        fila_ratio.addWidget(self.ratio_slider)
        chem_lay.addLayout(fila_ratio)

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

        # Aspecto visual
        vis_box = QGroupBox("Aspecto visual")
        vis_lay = QHBoxLayout(vis_box)

        self.combo_color = QComboBox()
        self.combo_transp = QComboBox()
        self.combo_brillo = QComboBox()

        for combo, label in (
            (self.combo_color, "Color"),
            (self.combo_transp, "Transparencia"),
            (self.combo_brillo, "Brillo"),
        ):
            v = QVBoxLayout()
            v.addWidget(QLabel(label))
            v.addWidget(combo)
            vis_lay.addLayout(v)

        col_der.addWidget(vis_box)

        col_der.addStretch()
        layout.addWidget(filtros_box, 3)

        # Datos
        self._cargar_vidriados()
        self._cargar_valores_visuales()

        # Conexiones
        self.lista.itemDoubleClicked.connect(self._abrir_detalle)
        self.btn_nuevo.clicked.connect(self._nuevo_vidriado)

        self.codigo_edit.textChanged.connect(self._aplicar_filtros)

        for slider in (
            self.temp_slider,
            self.si_slider,
            self.al_slider,
            self.ratio_slider,
        ):
            slider.rangeChanged.connect(lambda *_: self._aplicar_filtros())

        for chk in self._checks_fundentes.values():
            chk.stateChanged.connect(lambda *_: self._aplicar_filtros())

        for combo in (
            self.combo_color,
            self.combo_transp,
            self.combo_brillo,
        ):
            combo.currentIndexChanged.connect(self._aplicar_filtros)

    def _cargar_valores_visuales(self):
        colores = sorted({v.get("color") for v in self._vidriados if v.get("color")})
        transps = sorted({v.get("transparencia") for v in self._vidriados if v.get("transparencia")})
        brillos = sorted({v.get("brillo") for v in self._vidriados if v.get("brillo")})

        for combo, valores in (
            (self.combo_color, colores),
            (self.combo_transp, transps),
            (self.combo_brillo, brillos),
        ):
            combo.clear()
            combo.addItem("— cualquiera —")
            for v in valores:
                combo.addItem(v)

    def _cargar_vidriados(self):
        self._vidriados = self.controlador.obtener_lista_filtrable()
        self._refrescar_lista(self._vidriados)

    def _refrescar_lista(self, datos):
        self.lista.clear()
        for vid in datos:
            item = QListWidgetItem(vid.get("codigo", ""))
            item.setData(1, vid.get("id"))
            self.lista.addItem(item)
        self.contador.setText(str(len(datos)))

    def _aplicar_filtros(self):
        codigo_pref = self.codigo_edit.text().strip().upper()

        tmin, tmax = self.temp_slider.lower, self.temp_slider.upper
        simin, simax = self.si_slider.lower, self.si_slider.upper
        almin, almax = self.al_slider.lower, self.al_slider.upper
        rmin, rmax = self.ratio_slider.lower, self.ratio_slider.upper

        color_sel = self.combo_color.currentText()
        transp_sel = self.combo_transp.currentText()
        brillo_sel = self.combo_brillo.currentText()

        fundentes_activos = [
            ox for ox, chk in self._checks_fundentes.items() if chk.isChecked()
        ]

        filtrados = []

        for vid in self._vidriados:
            codigo = (vid.get("codigo") or "").upper()
            if codigo_pref and not codigo.startswith(codigo_pref):
                continue

            try:
                tval = float(vid.get("temperatura"))
            except Exception:
                continue
            if tval < tmin or tval > tmax:
                continue

            if color_sel != "— cualquiera —" and vid.get("color") != color_sel:
                continue
            if transp_sel != "— cualquiera —" and vid.get("transparencia") != transp_sel:
                continue
            if brillo_sel != "— cualquiera —" and vid.get("brillo") != brillo_sel:
                continue

            try:
                formula = json.loads(vid.get("formula", ""))
            except Exception:
                continue
            if not isinstance(formula, dict):
                continue

            si = formula.get("SiO2")
            al = formula.get("Al2O3")

            if si is None or si < simin or si > simax:
                continue
            if al is None or al < almin or al > almax:
                continue

            if al == 0:
                continue
            ratio = si / al
            if ratio < rmin or ratio > rmax:
                continue

            for ox in fundentes_activos:
                if formula.get(ox, 0.0) < 0.1:
                    break
            else:
                filtrados.append(vid)

        self._refrescar_lista(filtrados)

    def _abrir_detalle(self, item):
        vidriado_id = item.data(1)
        self.controlador.abrir_detalle(
            vidriado_id,
            on_change=self._cargar_vidriados
        )

    def _nuevo_vidriado(self):
        self.controlador.crear_nuevo(self)
