import math
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath, QRadialGradient, QConicalGradient, QPixmap, QPainter, QTransform

class ActionSector(QGraphicsPathItem):
    def __init__(self, player_x, player_y, ball_x, ball_y, scale=30):
        super().__init__()
        self.player_x = player_x
        self.player_y = player_y
        self.ball_x = ball_x
        self.ball_y = ball_y
        self.scale = scale
        self.max_radius = 4 * scale  # 4 meters max
        self.angle_width = 240  # sector width in degrees (each side)
        self.net_y = 9 * scale  # Y position of the net
        self.updatePosition(player_x, player_y, ball_x, ball_y)
        
    def updatePosition(self, player_x, player_y, ball_x, ball_y):
        self.player_x = player_x
        self.player_y = player_y
        self.ball_x = ball_x
        self.ball_y = ball_y
        self.draw_sector()
        
    def draw_sector(self):
        path = QPainterPath()
        
        # Calculate viewing direction angle based on ball position
        dx = self.ball_x - self.player_x
        dy = self.ball_y - self.player_y
        
        # Ensure we have a valid direction vector
        if dx == 0 and dy == 0:
            viewing_angle = 0  # Default angle if no direction
        else:
            viewing_angle = (-math.degrees(math.atan2(dy, dx))) % 360
        
        # Calculate start and end angles for the sector
        start_angle = viewing_angle - self.angle_width/2
        end_angle = viewing_angle + self.angle_width/2
        sweep_angle = self.angle_width
        
        # Calculate radius - either distance to net or max_radius, whichever is smaller
        distance_to_net = abs(self.net_y - self.player_y)
        radius = min(self.max_radius, distance_to_net)
        
        # Limit radius to court boundaries to avoid drawing outside
        radius = min(radius, self.scale * 20)  # Maximum 20 meters from player
        
        # Draw the sector
        path.moveTo(self.player_x, self.player_y)
        path.arcTo(self.player_x - radius, self.player_y - radius,
                   radius * 2, radius * 2,
                   start_angle, sweep_angle)
        path.lineTo(self.player_x, self.player_y)
        self.setPath(path)
        
        # Create a QPixmap for combined gradients
        size = int(radius * 2)
        if size <= 0:  # Avoid creating invalid pixmaps
            return
            
        combined = QPixmap(size, size)
        combined.fill(Qt.transparent)
        
        painter = QPainter(combined)
        # Radial gradient: from player position outward
        radial = QRadialGradient(QPointF(size/2, size/2), radius)
        radial.setColorAt(0.0, QColor(0, 255, 0, 180))   # Green near player
        radial.setColorAt(1.0, QColor(0, 255, 0, 0))     # Transparent at edges
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, size, size)
        
        # Conical gradient overlaying: direction based on viewing angle
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        conical = QConicalGradient(QPointF(size/2, size/2), viewing_angle)
        conical.setColorAt(0.0, QColor(0, 255, 0, 150))      # Green at viewing direction
        # Calculate color stops based on angle_width
        angle_fraction = self.angle_width/360
        conical.setColorAt(angle_fraction/2, QColor(0, 255, 0, 0))  # Transparent at edges
        conical.setColorAt(1 - angle_fraction/2, QColor(0, 255, 0, 0))
        conical.setColorAt(1.0, QColor(0, 255, 0, 150))      # Green again
        painter.setBrush(QBrush(conical))
        painter.drawRect(0, 0, size, size)
        painter.end()
        
        # Set opacity for the combined QPixmap
        temp = QPixmap(size, size)
        temp.fill(Qt.transparent)
        painter2 = QPainter(temp)
        painter2.setOpacity(0.5)
        painter2.drawPixmap(0, 0, combined)
        painter2.end()
        combined = temp
        
        # Position the brush correctly
        combined_brush = QBrush(combined)
        transform = QTransform()
        transform.translate(self.player_x - size/2, self.player_y - size/2)
        combined_brush.setTransform(transform)
        
        self.setBrush(combined_brush)
        self.setPen(QPen(Qt.NoPen))
