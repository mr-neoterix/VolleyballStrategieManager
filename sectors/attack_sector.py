import math
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath, QRadialGradient, QConicalGradient, QPixmap, QPainter, QTransform
from .base_sector import BaseSector

class AttackSector(BaseSector):
    def __init__(self, ball_pos, court_width=270, court_height=540, net_y=270, radius=300):
        super().__init__(ball_pos, z_index=2)
        self.ball_pos = ball_pos
        self.court_width = court_width
        self.court_height = court_height
        self.net_y = net_y
        self.radius = radius
        self.update_path()
        
    def updatePosition(self, ball_x, ball_y):
        # Absolute Szenenkoordinaten übernehmen
        self.ball_pos = QPointF(ball_x, ball_y)
        self.update_path()
        
    def update_path(self):
        path = QPainterPath()
        
        # Netzpositionen
        left_net = QPointF(0, self.net_y)
        right_net = QPointF(self.court_width, self.net_y)
        
        # Dynamischer Radius: Abstand vom Ballmittelpunkt zum unteren Spielfeldrand
        dynamic_radius = self.net_y * 2 - self.ball_pos.y()
        
        # Berechne Winkel basierend auf den Netzkanten und dem Ballmittelpunkt
        angle_left = math.degrees(math.atan2(self.ball_pos.y() - left_net.y(), 
                                            left_net.x() - self.ball_pos.x()))
        angle_right = math.degrees(math.atan2(self.ball_pos.y() - right_net.y(), 
                                            right_net.x() - self.ball_pos.x()))
        
        # Zeichne den Bogen
        start_angle = angle_left
        sweep_angle = angle_right - angle_left
        
        path.moveTo(self.ball_pos.x(), self.ball_pos.y())
        path.arcTo(self.ball_pos.x() - dynamic_radius, self.ball_pos.y() - dynamic_radius,
                dynamic_radius * 2, dynamic_radius * 2,
                start_angle, sweep_angle)
        path.lineTo(self.ball_pos.x(), self.ball_pos.y())
        self.setPath(path)
        
        # Gradients für den Attacksektor
        self._create_attack_gradient(dynamic_radius)
        
    def _create_attack_gradient(self, radius):
        # Erstelle ein QPixmap für die Gradienten
        size = int(radius * 2)
        if size <= 0:
            return
            
        combined = QPixmap(size, size)
        combined.fill(Qt.transparent)
        
        painter = QPainter(combined)
        # Radialer Gradient
        radial = QRadialGradient(QPointF(size/2, size/2), radius)
        radial.setColorAt(0.0, QColor(255, 0, 0, 255))   # Rot nahe am Ball
        radial.setColorAt(1.0, QColor(255, 255, 0, 255)) # Gelb
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, size, size)
        
        # Berechne den Winkel für konischen Gradienten
        bottom_center = QPointF(self.court_width/2, self.court_height)
        gradient_angle = (-math.degrees(math.atan2(
            bottom_center.y() - self.ball_pos.y(), 
            bottom_center.x() - self.ball_pos.x()
        ))) % 360
        
        # Konischer Gradient
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        conical = QConicalGradient(QPointF(size/2, size/2), gradient_angle)
        conical.setColorAt(0.0, QColor(255, 0, 0, 150))
        conical.setColorAt(0.1, QColor(255, 255, 0, 0))
        conical.setColorAt(0.9, QColor(255, 255, 0, 0))
        conical.setColorAt(1.0, QColor(255, 0, 0, 150))
        painter.setBrush(QBrush(conical))
        painter.drawRect(0, 0, size, size)
        painter.end()
        
        # Setze Opacity
        temp = QPixmap(size, size)
        temp.fill(Qt.transparent)
        painter2 = QPainter(temp)
        painter2.setOpacity(0.5)
        painter2.drawPixmap(0, 0, combined)
        painter2.end()
        combined = temp
        
        # Positioniere den Brush
        combined_brush = QBrush(combined)
        transform = QTransform()
        transform.translate(self.ball_pos.x() - size/2, self.ball_pos.y() - size/2)
        combined_brush.setTransform(transform)
        
        self.setBrush(combined_brush)
