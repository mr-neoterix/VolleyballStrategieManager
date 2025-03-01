import math
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QBrush, QColor, QPen, QPainterPath, QRadialGradient
from PyQt5.QtCore import QRectF, Qt, QPointF

# Use absolute imports instead of relative
from core import DraggableEllipse
from sectors.action_sector import ActionSector, ActionSectorParams
from utils import CourtDimensions

class PlayerItem(DraggableEllipse):
    def __init__(self, rect, label="", ball=None, court_dims=None):
        super().__init__(rect, label)
        # Set a very high z-value for the player itself
        self.setZValue(1000)  # Ensure player is always on top
        
        self.ball = ball  # Referenz zum Ball
        self.court_dims = court_dims or CourtDimensions()
        
        # Erstelle den Schlagschatten
        self.shadow = QGraphicsPathItem()
        self.shadow.setZValue(10)  # Higher than default but below player
        self.shadow.setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.shadow.setPen(QPen(Qt.NoPen))
        
        # Aktionssektoren
        self.sectors = {}
        
        # Initialisiere Aktionssektoren, wenn Ball vorhanden ist
        if ball:
            self.init_sectors()
            
    def init_sectors(self):
        if not self.ball:
            return
            
        # Erstelle die Aktionssektoren
        ball_rect = self.ball.rect()
        ball_center = self.ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
        player_center = self.scenePos() + self.rect().center()
        
        # Primary attack sector
        primary_params = ActionSectorParams(
            max_radius_meters=6,
            angle_width=35,
            color=QColor(0, 255, 0, 100)
        )
        self.sectors["primary"] = ActionSector(
            player_center, ball_center,
            params=primary_params,
            net_y=self.court_dims.net_y,
            z_index=5
        )
        
        # Wide action sector
        wide_params = ActionSectorParams(
            max_radius_meters=2, 
            angle_width=240,
            color=QColor(0, 255, 0, 100)  # Orange color
        )
        self.sectors["wide"] = ActionSector(
            player_center, ball_center,
            params=wide_params,
            net_y=self.court_dims.net_y,
            z_index=4
        )

        # Backward action sector
        backward_params = ActionSectorParams(
            max_radius_meters=1, 
            angle_width=120,
            color=QColor(0, 255, 0, 100),  # Purple color
            backwards=True
        )
        self.sectors["backward"] = ActionSector(
            player_center, ball_center,
            params=backward_params,
            net_y=self.court_dims.net_y,
            z_index=3
        )

    def updateShadow(self, ball_x, ball_y):
        player_center = self.scenePos() + self.rect().center()
        dx = player_center.x() - ball_x
        dy = player_center.y() - ball_y
        d = math.hypot(dx, dy)
        if d == 0:
            return
            
        # Spieler-Radius
        R = self.rect().width() / 2
        
        # Check if shadow should be shown
        if d + 2*R > 150:
            self.shadow.setPath(QPainterPath())
            # Auch wenn kein Schlagschatten gezeigt wird,
            # müssen wir trotzdem die Sektoren aktualisieren
        else:
            # Rest of shadow calculation
            theta = math.atan2(dy, dx)
            alpha = math.asin(min(R/d, 1))
            left_angle = theta - alpha
            right_angle = theta + alpha
            arc_radius = 250
            
            path = QPainterPath()
            path.moveTo(ball_x, ball_y)
            rect_arc = QRectF(ball_x - arc_radius, ball_y - arc_radius,
                             arc_radius * 2, arc_radius * 2)
            start_angle_deg = -math.degrees(left_angle)
            sweep_angle_deg = -math.degrees(right_angle - left_angle)
            path.arcTo(rect_arc, start_angle_deg, sweep_angle_deg)
            path.lineTo(ball_x, ball_y)
            self.shadow.setPath(path)
            
            # Create gradient for shadow
            gradient = QRadialGradient(QPointF(ball_x, ball_y), arc_radius)
            gradient.setColorAt(0.0, QColor(0, 255, 0, 0))
            fraction = d / arc_radius
            fraction = max(0, min(fraction, 1))
            gradient.setColorAt(fraction - 0.01, QColor(0, 255, 0, 0))
            gradient.setColorAt(fraction, QColor(0, 255, 0, 128))
            gradient.setColorAt(0.9, QColor(0, 255, 0, 128))
            gradient.setColorAt(1.0, QColor(0, 255, 0, 0))
            self.shadow.setBrush(QBrush(gradient))
        
        # Immer die Sektoren aktualisieren, unabhängig davon, 
        # ob ein Schlagschatten angezeigt wird oder nicht
        self.update_sectors(ball_x, ball_y)
    
    def update_sectors(self, ball_x, ball_y):
        player_center = self.scenePos() + self.rect().center()
        
        for sector in self.sectors.values():
            sector.updatePosition(player_center.x(), player_center.y(), ball_x, ball_y)
            if sector.scene():
                sector.scene().update(sector.boundingRect())
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        
        if self.ball:
            ball_rect = self.ball.rect()
            ball_center = self.ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
            self.updateShadow(ball_center.x(), ball_center.y())
            # Statt der Zeile unten sollten wir die update_sectors Funktion verwenden
            # self.update_action_sector(ball_center.x(), ball_center.y())  # Diese Zeile ist jetzt veraltet
            self.update_sectors(ball_center.x(), ball_center.y())
