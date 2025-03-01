from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPointF

class BaseSector(QGraphicsPathItem):
    def __init__(self, center=QPointF(), z_index=0):
        super().__init__()
        self.center = center
        self.path = QPainterPath()
        self.setZValue(z_index)
        self.setPen(QPen(Qt.NoPen))
        
    def set_center(self, x, y):
        self.center = QPointF(x, y)
        
    def update_path(self):
        """Override in subclasses to update the path"""
        pass
        
    def set_brush(self, brush):
        """Set the brush for this sector"""
        self.setBrush(brush)
