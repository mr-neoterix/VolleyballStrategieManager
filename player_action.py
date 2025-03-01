import math
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath, QRadialGradient

class ActionSector(QGraphicsPathItem):
    def __init__(self, player_x, player_y, ball_x, ball_y, scale=30, max_radius_meters=4, angle_width=40):
        super().__init__()
        self.player_x = player_x
        self.player_y = player_y
        self.ball_x = ball_x
        self.ball_y = ball_y
        self.scale = scale
        self.max_radius = max_radius_meters * scale  # Convert from meters to pixels
        self.angle_width = angle_width  # sector width in degrees
        self.net_y = 9 * scale  # Y position of the net (9 meters from the top)
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
            distance_to_intersection = self.max_radius
        else:
            viewing_angle = (-math.degrees(math.atan2(dy, dx))) % 360
            
            # Calculate intersection of player-ball line with the net line
            # First, determine if the line intersects with the net
            if self.player_y < self.net_y and self.ball_y < self.net_y:
                # Both player and ball are above the net, no intersection
                distance_to_intersection = self.max_radius
            elif self.player_y > self.net_y and self.ball_y > self.net_y:
                # Both player and ball are below the net, no intersection
                distance_to_intersection = self.max_radius
            else:
                # The line crosses the net, calculate intersection point
                if dy == 0:  # Horizontal line
                    intersection_x = self.player_x
                else:
                    # Calculate the x-coordinate where the line intersects the net
                    # Using the line equation: (x - x1) / (x2 - x1) = (y - y1) / (y2 - y1)
                    # Solving for x when y = net_y
                    intersection_x = self.player_x + (self.net_y - self.player_y) * dx / dy
                
                # Calculate distance from player to intersection point
                distance_to_intersection = math.sqrt(
                    (intersection_x - self.player_x) ** 2 + 
                    (self.net_y - self.player_y) ** 2
                )
                
                # Limit to max_radius if needed
                distance_to_intersection = min(distance_to_intersection, self.max_radius)
        
        # Calculate start and end angles for the sector
        start_angle = viewing_angle - self.angle_width/2
        end_angle = viewing_angle + self.angle_width/2
        sweep_angle = self.angle_width
        
        # Use the calculated radius
        radius = distance_to_intersection
        
        # Draw the sector
        path.moveTo(self.player_x, self.player_y)
        path.arcTo(self.player_x - radius, self.player_y - radius,
                   radius * 2, radius * 2,
                   start_angle, sweep_angle)
        path.lineTo(self.player_x, self.player_y)
        self.setPath(path)
        
        # Create a simple radial gradient from player outward
        gradient = QRadialGradient(QPointF(self.player_x, self.player_y), radius)
        
        # Green near player (opacity 150)
        gradient.setColorAt(0.0, QColor(0, 255, 0, 150))
        
        # Start fading at 70% of the radius
        gradient.setColorAt(0.7, QColor(0, 255, 0, 150))
        
        # Completely transparent at the edge
        gradient.setColorAt(1.0, QColor(0, 255, 0, 0))
        
        # Set as brush
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(Qt.NoPen))
