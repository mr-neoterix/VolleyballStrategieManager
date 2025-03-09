from PyQt6.QtCore import QPointF, QRectF, pyqtSignal, QObject
from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtGui import QBrush, QPen, QColor, QPainter

# Use absolute imports
from utils import CourtDimensions
from volleyball_field import players

class BallItem(QGraphicsObject):
    positionChanged = pyqtSignal(float, float)
    
    def __init__(self, rect, label="", court_dimensions=None, parent=None):
        super().__init__(parent)
        self._rect = rect
        self.setFlags(self.flags() | 
                      QGraphicsObject.GraphicsItemFlag.ItemIsSelectable | 
                      QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.court_dims = court_dimensions or CourtDimensions()
        self.half_court = self.court_dims.height / 2
        self.attack_sector = None
        # Set movement boundary for the ball (court boundaries)
        self.movement_boundary = QRectF(0, 0, self.court_dims.width, self.half_court)
        # ...existing code for appearance...
        self._brush = QBrush(QColor("yellow"))
        self._pen = QPen(QColor("black"), 2)
    
    def boundingRect(self):
        return self._rect
    
    def paint(self, painter: QPainter, option, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(self._rect)
    
    def link_sector(self, sector):
        self.attack_sector = sector
        self.update_sector_position()
    
    def update_sector_position(self):
        if self.attack_sector:
            center = self.scenePos() + QPointF(self._rect.width()/2, self._rect.height()/2)
            self.attack_sector.updatePosition(center.x(), center.y())
    
    def set_movement_boundary(self, boundary: QRectF):
        self.movement_boundary = boundary
    
    def setBrush(self, brush):
        self._brush = brush
        self.update()
        
    def setPen(self, pen):
        self._pen = pen
        self.update()
    
    def mouseMoveEvent(self, event):
        old_pos = self.pos()
        super().mouseMoveEvent(event)
        # Apply movement boundary constraints
        if self.movement_boundary:
            pos = self.pos()
            r = self.boundingRect()
            min_x = self.movement_boundary.x()
            max_x = self.movement_boundary.x() + self.movement_boundary.width() - r.width()
            new_x = max(min_x, min(pos.x(), max_x))
            min_y = self.movement_boundary.y()
            max_y = self.movement_boundary.y() + self.movement_boundary.height() - r.height()
            new_y = max(min_y, min(pos.y(), max_y))
            if new_x != pos.x() or new_y != pos.y():
                self.setPos(new_x, new_y)
        if old_pos != self.pos():
            ball_center = self.scenePos() + QPointF(self._rect.width()/2, self._rect.height()/2)
            self.update_sector_position()
            for player in players:
                player.updateShadow(ball_center.x(), ball_center.y())
            self.positionChanged.emit(ball_center.x(), ball_center.y())
