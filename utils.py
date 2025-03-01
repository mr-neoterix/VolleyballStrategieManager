import math
from PyQt5.QtCore import QPointF

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

def calculate_distance(p1, p2):
    """Calculate distance between two points"""
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    return math.sqrt(dx*dx + dy*dy)

def calculate_angle(from_point, to_point):
    """Calculate angle in degrees from one point to another"""
    dx = to_point.x() - from_point.x()
    dy = to_point.y() - from_point.y()
    return (-math.degrees(math.atan2(dy, dx))) % 360

def get_intersection_with_net(player_pos, ball_pos, net_y):
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
