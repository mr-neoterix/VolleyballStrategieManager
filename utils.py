import math
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF

# Constants
DEFAULT_SCALE = 30  # 30 pixels per meter

class CourtDimensions:
    def __init__(self, scale=DEFAULT_SCALE):
        self.scale = scale
        self.width = 9 * scale
        self.height = 18 * scale
        self.net_y = 9 * scale
        self.attack_line_y = self.net_y - 3 * scale
        self.defense_line_y = self.net_y + 3 * scale

def calculate_distance(p1: QPointF, p2: QPointF) -> float:
    """Calculate distance between two points"""
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    return math.sqrt(dx*dx + dy*dy)

def calculate_angle(from_point: QPointF, to_point: QPointF) -> float:
    """Calculate angle in degrees from one point to another"""
    dx = to_point.x() - from_point.x()
    dy = to_point.y() - from_point.y()
    return (-math.degrees(math.atan2(dy, dx))) % 360

def get_intersection_with_net(player_pos: QPointF, ball_pos: QPointF, net_y: float) -> QPointF:
    """Calculate intersection of player-ball line with the net"""
    dx = ball_pos.x() - player_pos.x()
    dy = ball_pos.y() - player_pos.y()
    
    # Check if both points are on the same side of the net
    if (player_pos.y() < net_y and ball_pos.y() < net_y) or \
       (player_pos.y() > net_y and ball_pos.y() > net_y):
        return None
    
    # Handle horizontal line case
    if dy == 0:
        return QPointF(player_pos.x(), net_y)
    
    # Calculate intersection using line equation
    intersection_x = player_pos.x() + (net_y - player_pos.y()) * dx / dy
    return QPointF(intersection_x, net_y)

class DraggableEllipse(QGraphicsEllipseItem):
    def __init__(self, rect, label=""):
        super().__init__(rect)
        self.setFlags(QGraphicsEllipseItem.ItemIsSelectable | QGraphicsEllipseItem.ItemIsMovable)
        self.setBrush(QBrush(QColor("blue")))
        self.setPen(QPen(Qt.black, 2))
        self.text_item = None
        if label:
            self.text_item = QGraphicsTextItem(label, self)
            font = self.text_item.font()
            original_size = font.pointSize() if font.pointSize() > 0 else 12
            font.setPointSize(original_size // 2)
            self.text_item.setFont(font)
            self.text_item.setDefaultTextColor(Qt.white)
            self.text_item.setPos(rect.x() + rect.width()/2 - self.text_item.boundingRect().width()/2,
                        rect.y() + rect.height()/2 - self.text_item.boundingRect().height()/2)
        self.movement_boundary: QRectF = None

    def set_movement_boundary(self, boundary: QRectF):
        self.movement_boundary = boundary

    def mouseMoveEvent(self, event):
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

    def update_label(self, new_label):
        if self.text_item:
            self.text_item.setPlainText(new_label)
            # Zentriere den Text neu
            rect = self.rect()
            self.text_item.setPos(rect.x() + rect.width()/2 - self.text_item.boundingRect().width()/2,
                                rect.y() + rect.height()/2 - self.text_item.boundingRect().height()/2)
