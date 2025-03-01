import math
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QBrush, QColor, QPen, QPainterPath, QRadialGradient
from PyQt5.QtCore import QRectF, Qt, QPointF
from core import DraggableEllipse

class PlayerItem(DraggableEllipse):
    def __init__(self, rect, label="", ball=None):
        super().__init__(rect, label)
        self.ball = ball  # Referenz zum Ball zur Berechnung des Schlagschattens
        # Erstelle den Schlagschatten als separates QGraphicsPathItem
        self.shadow = QGraphicsPathItem()
        self.shadow.setZValue(self.zValue() - 1)  # Hinter den Spieler legen
        self.shadow.setBrush(QBrush(QColor(0, 255, 0, 128)))  # Halbtransparentes Grün
        self.shadow.setPen(QPen(Qt.NoPen))

    def updateShadow(self, ball_x, ball_y):
        # Bestimme den Mittelpunkt des Spielers in Szenenkoordinaten.
        player_center = self.scenePos() + self.rect().center()
        dx = player_center.x() - ball_x
        dy = player_center.y() - ball_y
        d = math.hypot(dx, dy)
        if d == 0:
            return
        # Spieler-Radius (angenommen, der Spieler ist ein Kreis)
        R = self.rect().width() / 2
        # Wenn d - R > 150 (Schattenradius), ist der Spieler außerhalb des Schattenbereichs
        # und der Schatten muss entfernt werden
        if d + 2*R > 150:
            self.shadow.setPath(QPainterPath())
            return 
        # Winkel vom Ball zum Spielerzentrum
        theta = math.atan2(dy, dx)
        # Berechne den Tangentenwinkel (sicherstellen, dass R/d <= 1)
        alpha = math.asin(min(R/d, 1))
        left_angle = theta - alpha
        right_angle = theta + alpha
        # Hier verwenden wir einen konstanten Bogenradius für den Schatten (könnte auch dynamisch berechnet werden)
        arc_radius = 300
        path = QPainterPath()
        path.moveTo(ball_x, ball_y)
        rect_arc = QRectF(ball_x - arc_radius, ball_y - arc_radius,
                          arc_radius * 2, arc_radius * 2)
        # Invertiere die Winkel (Qt erwartet Winkel, bei denen 0° im 3-Uhr-Bereich liegt und
        # positive Winkel gegen den Uhrzeigersinn verlaufen)
        start_angle_deg = -math.degrees(left_angle)
        sweep_angle_deg = -math.degrees(right_angle - left_angle)
        path.arcTo(rect_arc, start_angle_deg, sweep_angle_deg)
        path.lineTo(ball_x, ball_y)
        self.shadow.setPath(path)
        
        # Erstelle den radialen Gradient:
        # Der Gradient ist zentriert am Ball (ball_x, ball_y) und hat als Radius arc_radius.
        # Er soll vom Ball (transparent) bis zum Spieler (halbtransparent grün) verlaufen.
        gradient = QRadialGradient(QPointF(ball_x, ball_y), arc_radius)
        gradient.setColorAt(0.0, QColor(0, 255, 0, 0))
        # Anteil des Übergangs: Spielerhinreichender Anteil (hier: d kann variiert werden)
        fraction = d / arc_radius
        fraction = max(0, min(fraction, 1))
        gradient.setColorAt(fraction - 0.01, QColor(0, 255, 0, 0))
        gradient.setColorAt(fraction, QColor(0, 255, 0, 128))
        gradient.setColorAt(0.9, QColor(0, 255, 0, 128))
        gradient.setColorAt(1.0, QColor(0, 255, 0, 0))
        self.shadow.setBrush(QBrush(gradient))
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Aktualisiere den Schlagschatten auch, wenn der Spieler bewegt wird.
        if self.ball:
            ball_rect = self.ball.rect()
            ball_center = self.ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
            self.updateShadow(ball_center.x(), ball_center.y())