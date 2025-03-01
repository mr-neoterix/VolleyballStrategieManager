from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QLineF

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
        wood_brush = QBrush(QColor(255, 169, 119, 100))  # Auftrag: SaddleBrown-ähnlich
        field_pen = QPen(Qt.black, 2)
        painter.setBrush(wood_brush)
        painter.setPen(field_pen)
        painter.drawRect(0, 0, self.court_width, self.court_length)

        # Zeichne das Netz (mit Überhang) als QLineF
        net_pen = QPen(Qt.black, 2)
        painter.setPen(net_pen)
        net_line = QLineF(-self.overhang, self.net_y, self.court_width + self.overhang, self.net_y)
        painter.drawLine(net_line)

        # Zeichne den Angriffsraum: Gestrichelte Linie 3 m (3 * scale) vom Netz entfernt (auf der Angriffsseite)
        attack_line_y = self.net_y - 3 * self.scale
        attack_pen = QPen(Qt.red, 2, Qt.DashLine)
        painter.setPen(attack_pen)
        attack_line = QLineF(0, attack_line_y, self.court_width, attack_line_y)
        painter.drawLine(attack_line)

        # Zeichne den Verteidigungsraum: Gestrichelte Linie 3 m (3 * scale) vom Netz entfernt im unteren Feld
        defense_line_y = self.net_y + 3 * self.scale
        defense_pen = QPen(Qt.red, 2, Qt.DashLine)
        painter.setPen(defense_pen)
        defense_line = QLineF(0, defense_line_y, self.court_width, defense_line_y)
        painter.drawLine(defense_line)