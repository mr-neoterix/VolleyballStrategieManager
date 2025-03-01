import math
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QColor, QPen, QPainterPath, QRadialGradient

# Use absolute imports
from sectors.base_sector import BaseSector
from utils import get_intersection_with_net, calculate_angle

class ActionSectorParams:
    """Parameters for creating an action sector"""
    def __init__(self, max_radius_meters=4, angle_width=40, color=QColor(0, 255, 0, 150), backwards=False):
        self.max_radius_meters = max_radius_meters
        self.angle_width = angle_width
        self.color = color
        self.backwards = backwards

class ActionSector(BaseSector):
    def __init__(self, player_pos, ball_pos, params=None, scale=30, net_y=270, z_index=5):
        super().__init__(player_pos, z_index)
        self.player_pos = player_pos
        self.ball_pos = ball_pos
        self.params = params or ActionSectorParams()
        self.scale = scale
        self.net_y = net_y
        self.max_radius = self.params.max_radius_meters * scale
        self.update_path()
        
    def updatePosition(self, player_x, player_y, ball_x, ball_y):
        self.player_pos = QPointF(player_x, player_y)
        self.ball_pos = QPointF(ball_x, ball_y)
        self.update_path()
        
    def update_path(self):
        path = QPainterPath()
        
        # Calculate viewing direction angle based on ball position
        if self.params.backwards:
            # Calculate angle from ball to player (opposite direction)
            viewing_angle = (calculate_angle(self.ball_pos, self.player_pos)) % 360
        else:
            viewing_angle = calculate_angle(self.player_pos, self.ball_pos)
        
        # Get distance to intersection with net, or max_radius if no intersection
        distance_to_intersection = self.max_radius
        
        # If player and ball aren't at the same position
        if self.player_pos != self.ball_pos:
            intersection = get_intersection_with_net(self.player_pos, self.ball_pos, self.net_y)
            if intersection:
                # Calculate distance from player to intersection point
                dx = intersection.x() - self.player_pos.x()
                dy = intersection.y() - self.player_pos.y()
                distance_to_intersection = math.sqrt(dx*dx + dy*dy)
                # Limit to max_radius if needed
                distance_to_intersection = min(distance_to_intersection, self.max_radius)
        
        # Calculate start and end angles for the sector
        start_angle = viewing_angle - self.params.angle_width/2
        sweep_angle = self.params.angle_width
        
        # Use the calculated radius
        radius = distance_to_intersection
        
        # Draw the sector
        path.moveTo(self.player_pos.x(), self.player_pos.y())
        path.arcTo(self.player_pos.x() - radius, self.player_pos.y() - radius,
                radius * 2, radius * 2,
                start_angle, sweep_angle)
        path.lineTo(self.player_pos.x(), self.player_pos.y())
        self.setPath(path)
        
        # Create a simple radial gradient from player outward
        gradient = QRadialGradient(self.player_pos, radius)
        
        # Base color near player
        gradient.setColorAt(0.0, self.params.color)
        
        # Start fading at 70% of the radius
        gradient.setColorAt(0.7, self.params.color)
        
        # Completely transparent at the edge
        transparent_color = QColor(self.params.color)
        transparent_color.setAlpha(0)
        gradient.setColorAt(1.0, transparent_color)
        
        # Set as brush
        self.setBrush(QBrush(gradient))
