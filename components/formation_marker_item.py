from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import Qt, QRectF

class FormationMarkerItem(QGraphicsEllipseItem):
    """A small circular marker to indicate saved ball positions on the court."""
    
    def __init__(self, ball_pos, formation_index, radius=3):  # Smaller radius (was 5)
        """
        Create a marker at the ball position.
        
        Args:
            ball_pos: Tuple (x, y) with ball coordinates
            formation_index: Index of the formation in the list
            radius: Radius of the marker in pixels
        """
        diameter = radius * 2
        super().__init__(-radius, -radius, diameter, diameter)
        
        self.formation_index = formation_index
        self.setPos(ball_pos[0], ball_pos[1])
        
        # Set appearance - transparent fill, just red border
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))  # Create a QBrush with NoBrush style
        self.setPen(QPen(QColor("red"), 1))          # Red border
        
        # Use a lower z-value than the ball but higher than the court
        self.setZValue(100)
        
        # Make it non-interactive
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, False)
