from PyQt5.QtCore import QPointF, QRectF

# Use absolute imports
from core import DraggableEllipse, players
from utils import CourtDimensions

class BallItem(DraggableEllipse):
    def __init__(self, rect, label="", court_dimensions=None):
        super().__init__(rect, label)
        self.court_dims = court_dimensions or CourtDimensions()
        self.half_court = self.court_dims.height / 2
        self.attack_sector = None
        # New: Set movement boundary for the ball (court boundaries)
        boundary = QRectF(0, 0, self.court_dims.width, self.half_court)
        self.set_movement_boundary(boundary)

    def link_sector(self, sector):
        self.attack_sector = sector
        self.update_sector_position()

    def update_sector_position(self):
        if self.attack_sector:
            ball_rect = self.rect()
            center = self.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
            self.attack_sector.updatePosition(center.x(), center.y())

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        ball_rect = self.rect()
        ball_center = self.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
        self.update_sector_position()
        
        # Update player shadows and sectors
        for player in players:
            player.updateShadow(ball_center.x(), ball_center.y())
