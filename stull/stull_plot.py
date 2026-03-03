# -----------------------------------------------------------------------------
# 10_stull_plot.py
#
# Ventana independiente del diagrama Stull (cartesiano).
#
# Características:
# - No modal
# - Ejes fijos (0–8 SiO2 / 0–2 Al2O3)
# - Puntos gris claro uniforme
# - Tooltip con brillo + fundentes individuales
# - Botones 4 / 8 / 12 para mostrar/ocultar rectas
#     correspondientes a relaciones SiO2 / Al2O3
#
# Encapsulado. No accede a base de datos.
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


FUNDENTES_TOOLTIP = [
    "Li2O", "Na2O", "K2O",
    "MgO", "CaO", "SrO",
    "BaO", "ZnO", "PbO",
    "B2O3"
]


class StullPlot(QDialog):
    """Ventana no modal del diagrama Stull con líneas de proporción."""

    RATIOS = [4, 8, 12]

    def __init__(self, puntos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diagrama Stull")
        self.resize(800, 600)

        self._puntos = puntos
        self._scatter_data = []
        self._lineas_ratio = {}

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)

        # Botones superiores
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()

        self._ratio_buttons = {}

        for r in self.RATIOS:
            btn = QPushButton(str(r))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, ratio=r: self._toggle_ratio(ratio))
            botones_layout.addWidget(btn)
            self._ratio_buttons[r] = btn

        layout.addLayout(botones_layout)
        layout.addWidget(self.canvas)

        self._annot = None
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)

        self._dibujar()

    # ------------------------------------------------------------------

    def actualizar_puntos(self, puntos):
        self._puntos = puntos
        self._dibujar()

    # ------------------------------------------------------------------

    def _dibujar(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.set_xlim(0, 8)
        ax.set_ylim(0, 2)

        bd_x, bd_y = [], []
        currie_x, currie_y = [], []

        self._scatter_data = []

        for p in self._puntos:
            x = p.get("sio2", 0.0)
            y = p.get("al2o3", 0.0)

            if p.get("tipo") == "currie":
                currie_x.append(x)
                currie_y.append(y)
            else:
                bd_x.append(x)
                bd_y.append(y)

            self._scatter_data.append((x, y, p))

        color = "#BFBFBF"

        if bd_x:
            ax.scatter(bd_x, bd_y, marker="o", color=color)

        if currie_x:
            ax.scatter(currie_x, currie_y, marker="^", color=color)

        # Redibujar líneas activas
        for ratio in self._lineas_ratio:
            self._draw_ratio_line(ax, ratio)

        ax.set_xlabel("SiO₂ (UMF)")
        ax.set_ylabel("Al₂O₃ (UMF)")
        ax.set_title("Diagrama Stull")
        ax.grid(True)

        self._annot = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", ec="black"),
            arrowprops=dict(arrowstyle="->")
        )
        self._annot.set_visible(False)

        self.canvas.draw()

    # ------------------------------------------------------------------

    def _toggle_ratio(self, ratio):
        if ratio in self._lineas_ratio:
            del self._lineas_ratio[ratio]
        else:
            self._lineas_ratio[ratio] = True

        self._dibujar()

    # ------------------------------------------------------------------

    def _draw_ratio_line(self, ax, ratio):
        # Relación: SiO2 / Al2O3 = ratio  →  SiO2 = ratio * Al2O3
        y_vals = [0, 2]
        x_vals = [ratio * y for y in y_vals]

        ax.plot(x_vals, y_vals, linestyle="--", color="#999999")

    # ------------------------------------------------------------------

    def _on_hover(self, event):
        if event.inaxes is None or not self._scatter_data:
            if self._annot:
                self._annot.set_visible(False)
                self.canvas.draw_idle()
            return

        x_mouse, y_mouse = event.xdata, event.ydata
        threshold = 0.08

        for x, y, punto in self._scatter_data:
            if abs(x - x_mouse) < threshold and abs(y - y_mouse) < threshold:

                formula = punto.get("formula", {})
                codigo = punto.get("codigo", "")
                brillo = punto.get("brillo", "")

                lineas = []

                if codigo:
                    lineas.append(f"Código: {codigo}")

                if brillo:
                    lineas.append(f"Brillo: {brillo}")

                for ox in FUNDENTES_TOOLTIP:
                    valor = formula.get(ox, 0.0)
                    if valor > 0:
                        lineas.append(f"{ox}: {valor:.3f}")

                texto = "\n".join(lineas) if lineas else "Sin datos"

                self._annot.xy = (x, y)
                self._annot.set_text(texto)
                self._annot.set_visible(True)
                self.canvas.draw_idle()
                return

        self._annot.set_visible(False)
        self.canvas.draw_idle()
