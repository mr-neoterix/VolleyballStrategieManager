from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF

# Globale Liste für Spieler (PlayerItems)
players = []

# Klasse für bewegliche (draggable) Kreise
class DraggableEllipse(QGraphicsEllipseItem):
    def __init__(self, rect, label=""):
        super().__init__(rect)
        # Flags setzen, damit der Artikel mit der Maus bewegt werden kann
        self.setFlags(QGraphicsEllipseItem.ItemIsSelectable | QGraphicsEllipseItem.ItemIsMovable)
        # Standardfarbe (kann später überschrieben werden)
        self.setBrush(QBrush(QColor("blue")))
        self.setPen(QPen(Qt.black, 2))
        # Beschriftung hinzufügen
        if label:
            text = QGraphicsTextItem(label, self)
            text.setDefaultTextColor(Qt.white)
            # Zentriere die Beschriftung innerhalb des Kreises
            text.setPos(rect.x() + rect.width()/2 - text.boundingRect().width()/2,
                        rect.y() + rect.height()/2 - text.boundingRect().height()/2)
        self.movement_boundary: QRectF = None  # New: movement constraints

    def set_movement_boundary(self, boundary: QRectF):
        self.movement_boundary = boundary

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.movement_boundary:
            pos = self.pos()
            r = self.rect()
            # Calculate allowed x
            min_x = self.movement_boundary.x()
            max_x = self.movement_boundary.x() + self.movement_boundary.width() - r.width()
            new_x = max(min_x, min(pos.x(), max_x))
            # Calculate allowed y
            min_y = self.movement_boundary.y()
            max_y = self.movement_boundary.y() + self.movement_boundary.height() - r.height()
            new_y = max(min_y, min(pos.y(), max_y))
            if new_x != pos.x() or new_y != pos.y():
                self.setPos(new_x, new_y)