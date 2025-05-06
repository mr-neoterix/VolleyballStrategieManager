from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import Qt, QRectF, QLineF

class VolleyballField(QGraphicsItem):
    def __init__(self, scale=30, parent=None):
        super().__init__(parent)
        self.scale = scale
        self.court_width = 9 * scale
        self.court_length = 18 * scale
        self.net_y = self.court_length / 2
        self.overhang = 20  # Pixelüberhang an beiden Seiten
        # Setze Z-Wert so niedrig, dass das Feld immer im Hintergrund liegt.
        self.setZValue(-1000)

    def boundingRect(self):
        # Berücksichtige den Überhang
        return QRectF(-self.overhang, 0, self.court_width + 2*self.overhang, self.court_length)

    def paint(self, painter, option, widget):
        # Färbe den Spielfeldboden in einer Holzfarbe (z. B. ein heller Holzton)
        wood_brush = QBrush(QColor(255, 169, 129, 100))  # Auftrag: SaddleBrown-ähnlich
        field_pen = QPen(QColor("black"), 2)
        painter.setBrush(wood_brush)
        painter.setPen(field_pen)
        painter.drawRect(0, 0, self.court_width, self.court_length)

        # Zeichne das Netz (mit Überhang) als QLineF
        net_pen = QPen(QColor("grey"), 2)
        painter.setPen(net_pen)
        net_line = QLineF(-self.overhang, self.net_y, self.court_width + self.overhang, self.net_y)
        painter.drawLine(net_line)

        # Zeichne 3-Meter-Linien als festen Bestandteil des Spielfelds
        line_pen = QPen(QColor("red"), 2, Qt.PenStyle.DashLine)
        painter.setPen(line_pen)
        # 3-Meter-Linie vor dem Netz
        y_attack = self.net_y - 3 * self.scale
        painter.drawLine(QLineF(0, y_attack, self.court_width, y_attack))
        # 3-Meter-Linie hinter dem Netz
        y_defense = self.net_y + 3 * self.scale
        painter.drawLine(QLineF(0, y_defense, self.court_width, y_defense))

# Add global player list for VolleyballField
players = []