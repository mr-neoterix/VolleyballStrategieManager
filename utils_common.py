# Diese Datei enthält gemeinsame Hilfsfunktionen für das Volleyballprojekt
import math
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import Qt, QRectF

# Konstante
DEFAULT_SCALE = 30  # 30 Pixel pro Meter

class CourtDimensions: #standardmaße für das volleyballfeld
    def __init__(self, scale=DEFAULT_SCALE):
        self.scale = scale
        self.width = 9 * scale
        self.height = 18 * scale 
        self.net_y = 9 * scale
        self.attack_line_y = self.net_y - 3 * scale
        self.defense_line_y = self.net_y + 3 * scale

def calculate_distance(p1: QPointF, p2: QPointF) -> float:
    """Berechnet den Abstand zwischen zwei Punkten"""
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    return math.sqrt(dx*dx + dy*dy)

def calculate_angle(from_point: QPointF, to_point: QPointF) -> float:
    """Berechnet den Winkel in Grad von einem Punkt zu einem anderen"""
    dx = to_point.x() - from_point.x()
    dy = to_point.y() - from_point.y()
    return (-math.degrees(math.atan2(dy, dx))) % 360

def get_intersection_with_net(player_pos: QPointF, ball_pos: QPointF, net_y: float) -> QPointF: 
    """Berechnet den Schnittpunkt der Linie zwischen Spieler und Ball mit dem Netz"""
    dx = ball_pos.x() - player_pos.x()
    dy = ball_pos.y() - player_pos.y()
    
    # Prüft, ob beide Punkte auf der gleichen Seite des Netzes sind
    if (player_pos.y() < net_y and ball_pos.y() < net_y) or \
       (player_pos.y() > net_y and ball_pos.y() > net_y):
        return None
    
    if dy == 0: #wenn ball und spieler auf netzt liegen 
        return QPointF(player_pos.x(), net_y) 
    
    # Berechnet den Schnittpunkt mit der Geradengleichung
    intersection_x = player_pos.x() + (net_y - player_pos.y()) * dx / dy
    return QPointF(intersection_x, net_y) # wichtig für die spielerposition  

class DraggableEllipse(QGraphicsEllipseItem):
    def __init__(self, rect, label=""):
        super().__init__(rect)
        # Setzt Flag für bewegbare Grafikelemente in PyQt6
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable) #wird eingestellt, dass die Ellipse bewegt werden kann  
        self.setBrush(QBrush(QColor("blue")))
        # Verwendet QColor("black") statt Qt.black
        self.setPen(QPen(QColor("black"), 2))
        if label:
            text = QGraphicsTextItem(label, self)   
            font = text.font()
            original_size = font.pointSize() if font.pointSize() > 0 else 12 #12 ist die Schriftgröße   
            font.setPointSize(original_size // 2)
            text.setFont(font)
            text.setDefaultTextColor(QColor("white"))
            text.setPos(rect.x() + rect.width()/2 - text.boundingRect().width()/2,
                        rect.y() + rect.height()/2 - text.boundingRect().height()/2)
        self.movement_boundary: QRectF = None

    def set_movement_boundary(self, boundary: QRectF):
        self.movement_boundary = boundary

    def mouseMoveEvent(self, event):    #wird ausgelöst, wenn ellipse bewegt wird  
        super().mouseMoveEvent(event)
        if self.movement_boundary:
            pos = self.pos()
            r = self.rect()
            min_x = self.movement_boundary.x()
            max_x = self.movement_boundary.x() + self.movement_boundary.width() - r.width()
            new_x = max(min_x, min(pos.x(), max_x))
            min_y = self.movement_boundary.y()
            max_y = self.movement_boundary.y() + self.movement_boundary.height() - r.height()
            new_y = max(min_y, min(pos.y(), max_y))
            if new_x != pos.x() or new_y != pos.y():
                self.setPos(new_x, new_y)
