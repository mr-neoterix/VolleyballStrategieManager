from PyQt5.QtCore import QPointF

# Use absolute imports
from core import DraggableEllipse
from utils import CourtDimensions

class BallItem(DraggableEllipse):
    def __init__(self, rect, label="", court_dimensions=None):
        super().__init__(rect, label)
        self.court_dims = court_dimensions or CourtDimensions()
        self.half_court = self.court_dims.height / 2
        self.attack_sector = None

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
        current_pos = self.scenePos()
        new_pos = QPointF(current_pos)
        needs_update = False

        # Constrain ball position to court boundaries
        if current_pos.x() < 0:
            new_pos.setX(0)
            needs_update = True
        if current_pos.x() + ball_rect.width() > self.court_dims.width:
            new_pos.setX(self.court_dims.width - ball_rect.width())
            needs_update = True
        if current_pos.y() < 0:
            new_pos.setY(0)
            needs_update = True
        if current_pos.y() + ball_rect.height() > self.half_court:
            new_pos.setY(self.half_court - ball_rect.height())
            needs_update = True

        if needs_update:
            self.setPos(new_pos)

        ball_center = new_pos + QPointF(ball_rect.width()/2, ball_rect.height()/2)

        self.update_sector_position()
        
        # Update player shadows and sectors
        from core import players  # Use absolute import here too
        for player in players:
            player.updateShadow(ball_center.x(), ball_center.y())
