import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainterPath, QRadialGradient, QPixmap, QPainter, QTransform
from .base_sector import BaseSector

class AttackSector(BaseSector):
    def __init__(self, ball_pos:QPointF, court_width=270, court_height=540, net_y=270, radius=300):
        super().__init__(ball_pos, z_index=2)
        self.ball_pos = ball_pos
        self.court_width = court_width
        self.court_height = court_height
        self.net_y = net_y
        self.radius = radius
        self.update_path()
        
    def updatePosition(self, ball_x, ball_y):
        # Aktualisiert die Ballposition mit den angegebenen Koordinaten
        self.ball_pos = QPointF(ball_x, ball_y)
        self.update_path()
        
    def update_path(self):
        path = QPainterPath()
        
        # Definiert die Positionen der Netzenden
        left_net = QPointF(0, self.net_y)
        right_net = QPointF(self.court_width, self.net_y)
        
        # Dynamischer Radius: Berechnet den verfügbaren Platz vom Ball zum unteren Spielfeldrand
        dynamic_radius = self.net_y * 2 - self.ball_pos.y()
        
        # Berechnet die Winkel vom Ball zu den beiden Netzenden
        # Diese Winkel bestimmen die Grenzen des Angriffssektors
        angle_left = math.degrees(math.atan2(self.ball_pos.y() - left_net.y(), 
                                            left_net.x() - self.ball_pos.x()))
        angle_right = math.degrees(math.atan2(self.ball_pos.y() - right_net.y(), 
                                            right_net.x() - self.ball_pos.x()))
        
        # Zeichnet den Bogen des Angriffssektors
        start_angle = angle_left
        sweep_angle = angle_right - angle_left
        
        path.moveTo(self.ball_pos.x(), self.ball_pos.y())
        path.arcTo(self.ball_pos.x() - dynamic_radius, self.ball_pos.y() - dynamic_radius,
                dynamic_radius * 2, dynamic_radius * 2,
                start_angle, sweep_angle)
        path.lineTo(self.ball_pos.x(), self.ball_pos.y())
        self.setPath(path)
        
        # Erstellt den Farbverlauf für den Angriffssektor
        self._create_attack_gradient(dynamic_radius)
        
    def _create_attack_gradient(self, radius):
        # Erstellt eine Zeichenfläche für den Farbverlauf
        size = int(radius * 2)
        if size <= 0:
            return
            
        combined = QPixmap(size, size)
        combined.fill(QColor(0, 0, 0, 0))  # Transparenter Hintergrund
        
        painter = QPainter(combined)
        # Erzeugt einen radialen Farbverlauf vom Ball nach außen
        radial = QRadialGradient(QPointF(size/2, size/2), radius)
        radial.setColorAt(0.0, QColor(255, 0, 0, 255))   # Rot nahe am Ball (hohe Angriffsintensität)
        radial.setColorAt(1.0, QColor(255, 255, 0, 255)) # Gelb am Rand (niedrigere Intensität)
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, size, size)
        painter.end()
        
        # Fügt Transparenz hinzu (50%)
        temp = QPixmap(size, size)
        temp.fill(QColor(0, 0, 0, 0))  # Transparenter Hintergrund
        painter2 = QPainter(temp)
        painter2.setOpacity(0.5)
        painter2.drawPixmap(0, 0, combined)
        painter2.end()
        combined = temp
        
        # Positioniert den Farbverlauf auf dem Spielfeld passend zur Ballposition
        combined_brush = QBrush(combined)
        transform = QTransform()
        transform.translate(self.ball_pos.x() - size/2, self.ball_pos.y() - size/2)
        combined_brush.setTransform(transform)
        
        self.setBrush(combined_brush)
