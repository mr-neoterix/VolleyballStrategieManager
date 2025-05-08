from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import Qt, QRectF

class FormationMarkerItem(QGraphicsEllipseItem):
    """Ein kleiner kreisförmiger Marker, der gespeicherte Ballpositionen auf dem Spielfeld anzeigt."""
    
    def __init__(self, ball_pos, formation_index, radius=3):  # Kleinerer Radius (war 5)
        """
        Erstellt einen Marker an der Ballposition.
        
        Parameter:
            ball_pos: Tupel (x, y) mit den Ballkoordinaten
            formation_index: Index der Formation in der Liste
            radius: Radius des Markers in Pixel
        """
        diameter = radius * 2
        super().__init__(-radius, -radius, diameter, diameter)
        
        self.formation_index = formation_index
        self.setPos(ball_pos[0], ball_pos[1])
        
        # Setzt das Aussehen - transparente Füllung, nur roter Rand
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))  # Erstellt einen QBrush ohne Füllung
        self.setPen(QPen(QColor("red"), 1))          # Roter Rand
        
        # Verwendet einen niedrigeren Z-Wert als der Ball, aber höher als das Spielfeld
        self.setZValue(100)
        
        # Macht den Marker nicht interaktiv
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, False)
