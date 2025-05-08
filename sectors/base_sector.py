from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui import QPen, QPainterPath
from PyQt6.QtCore import Qt, QPointF

class BaseSector(QGraphicsPathItem):
    def __init__(self, center:QPointF=QPointF(), z_index=0):
        super().__init__()
        self.center = center
        self.path = QPainterPath()
        self.setZValue(z_index)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        
    def set_center(self, x, y):
        self.center = QPointF(x, y)
        
    def update_path(self):
        """In Unterklassen überschreiben, um den Pfad zu aktualisieren"""
        pass
        
    def set_brush(self, brush):
        """Legt den Pinsel (Füllstil) für diesen Sektor fest"""
        self.setBrush(brush)
