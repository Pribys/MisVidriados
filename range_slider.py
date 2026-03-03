from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class RangeSlider(QWidget):
    """Slider de rango con dos manejadores (valores decimales).
    - Rango fijo [minimum, maximum]
    - Dos valores seleccionables: lower, upper (float)
    - Precisión configurable
    - Emite señal rangeChanged(lower, upper)
    """

    rangeChanged = Signal(float, float)

    def __init__(
        self,
        minimum,
        maximum,
        lower=None,
        upper=None,
        precision=2,
        parent=None,
    ):
        super().__init__(parent)

        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.precision = int(precision)

        self.lower = self.minimum if lower is None else float(lower)
        self.upper = self.maximum if upper is None else float(upper)

        self._handle_radius = 8
        self._bar_height = 6
        self._active_handle = None

        self.setMinimumHeight(55)

    # ───── Utilidades ─────

    def _value_to_pos(self, value):
        w = self.width() - 2 * self._handle_radius
        return self._handle_radius + (value - self.minimum) / (self.maximum - self.minimum) * w

    def _pos_to_value(self, x):
        w = self.width() - 2 * self._handle_radius
        x = min(max(x - self._handle_radius, 0), w)
        val = self.minimum + (x / w) * (self.maximum - self.minimum)
        return round(val, self.precision)

    def _fmt(self, value):
        return f"{value:.{self.precision}f}"

    # ───── Pintado ─────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        bar_y = self.height() // 2

        # Barra base
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(210, 210, 210))
        p.drawRoundedRect(
            QRectF(
                self._handle_radius,
                bar_y - self._bar_height / 2,
                self.width() - 2 * self._handle_radius,
                self._bar_height
            ),
            3, 3
        )

        # Barra activa
        x1 = self._value_to_pos(self.lower)
        x2 = self._value_to_pos(self.upper)
        p.setBrush(QColor(90, 150, 210))
        p.drawRoundedRect(
            QRectF(x1, bar_y - self._bar_height / 2, x2 - x1, self._bar_height),
            3, 3
        )

        # Manejadores
        p.setBrush(QColor(40, 40, 40))
        for x in (x1, x2):
            p.drawEllipse(
                QRectF(
                    x - self._handle_radius,
                    bar_y - self._handle_radius,
                    2 * self._handle_radius,
                    2 * self._handle_radius
                )
            )

        # Texto
        font = QFont()
        font.setPointSize(8)
        p.setFont(font)
        p.setPen(QPen(Qt.black))

        # Extremos
        p.drawText(2, bar_y + 22, self._fmt(self.minimum))
        p.drawText(self.width() - 50, bar_y + 22, self._fmt(self.maximum))

        # Valores actuales
        p.drawText(x1 - 18, bar_y - 16, self._fmt(self.lower))
        p.drawText(x2 - 18, bar_y - 16, self._fmt(self.upper))

    # ───── Ratón ─────

    def mousePressEvent(self, event):
        x = event.position().x()
        x1 = self._value_to_pos(self.lower)
        x2 = self._value_to_pos(self.upper)
        self._active_handle = 'lower' if abs(x - x1) < abs(x - x2) else 'upper'

    def mouseMoveEvent(self, event):
        if not self._active_handle:
            return

        val = self._pos_to_value(event.position().x())

        if self._active_handle == 'lower':
            self.lower = min(max(self.minimum, val), self.upper)
        else:
            self.upper = max(min(self.maximum, val), self.lower)

        self.rangeChanged.emit(self.lower, self.upper)
        self.update()

    def mouseReleaseEvent(self, event):
        self._active_handle = None
