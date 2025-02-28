from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt

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