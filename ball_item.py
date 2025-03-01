import math
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath, QRadialGradient, QConicalGradient, QPixmap, QPainter, QTransform
from core import DraggableEllipse

class BallItem(DraggableEllipse):
    def __init__(self, rect, sector=None, label="", court_dimensions=None):
        super().__init__(rect, label)
        self.sector = sector
        self.court_dimensions = court_dimensions or {"width": 9*30, "height": 18*30}
        self.half_court = self.court_dimensions["height"] / 2

    def link_sector(self, sector):
        self.sector = sector
        self.update_sector_position()

    def update_sector_position(self):
        if self.sector:
            ball_rect = self.rect()
            center = self.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
            self.sector.updatePosition(center.x(), center.y())

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        ball_rect = self.rect()
        current_pos = self.scenePos()
        new_pos = QPointF(current_pos)
        needs_update = False

        if current_pos.x() < 0:
            new_pos.setX(0)
            needs_update = True
        if current_pos.x() + ball_rect.width() > self.court_dimensions["width"]:
            new_pos.setX(self.court_dimensions["width"] - ball_rect.width())
            needs_update = True
        if current_pos.y() < 0:
            new_pos.setY(0)
            needs_update = True
        if current_pos.y() + ball_rect.height() > self.half_court:
            new_pos.setY(self.half_court - ball_rect.height())
            needs_update = True

        if needs_update:
            self.setPos(new_pos)

        ball_center = new_pos + QPointF(ball_rect.width()/2, ball_rect.height()/2)

        self.update_sector_position()
        # Aktualisiere auch alle Spieler-Schlagschatten (z.B. über eine globale Liste)
        from core import players  # falls du players global in players.py oder main verwaltest
        for player in players:
            player.updateShadow(ball_center.x(), ball_center.y())

# Neue Klasse für den Schlagsektor (Winkelbereich der möglichen Schlagrichtungen)
class AttackSector(QGraphicsPathItem):
    def __init__(self, ball_x, ball_y, radius=300):
        super().__init__()
        self.ball_x = ball_x
        self.ball_y = ball_y
        self.radius = radius  # Wird dynamisch überschrieben
        self.draw_sector()
        
    def updatePosition(self, ball_x, ball_y):
        # Absolute Szenenkoordinaten übernehmen
        self.ball_x = ball_x
        self.ball_y = ball_y
        self.draw_sector()
        
    def draw_sector(self):
        path = QPainterPath()
        # Spielfeldparameter (scale=30)
        court_width = 9 * 30
        court_height = 18 * 30
        net_y = 270  # Untere Grenze des Angriffsbereichs (Netz)
        left_net = QPointF(0, net_y)
        right_net = QPointF(court_width, net_y)
        
        # Dynamischer Radius: Abstand vom Ballmittelpunkt zum unteren Spielfeldrand (net_y * 2)
        dynamic_radius = net_y * 2 - self.ball_y
        
        # Berechne Winkel basierend auf den Netzkanten und dem Ballmittelpunkt.
        angle_left = math.degrees(math.atan2(self.ball_y - left_net.y(), left_net.x() - self.ball_x))
        angle_right = math.degrees(math.atan2(self.ball_y - right_net.y(), right_net.x() - self.ball_x))
        
        # Zeichne den Bogen: Starte beim linken Winkel und fahre bis zum rechten Winkel
        start_angle = angle_left
        sweep_angle = angle_right - angle_left
        
        path.moveTo(self.ball_x, self.ball_y)
        path.arcTo(self.ball_x - dynamic_radius, self.ball_y - dynamic_radius,
                   dynamic_radius * 2, dynamic_radius * 2,
                   start_angle, sweep_angle)
        path.lineTo(self.ball_x, self.ball_y)
        self.setPath(path)
        
        # Erstelle ein QPixmap, um beide Gradienten zu kombinieren.
        size = int(dynamic_radius * 2)
        combined = QPixmap(size, size)
        combined.fill(Qt.transparent)
        
        painter = QPainter(combined)
        # Radialer Gradient: vom Ballmittelpunkt nach außen
        radial = QRadialGradient(QPointF(size/2, size/2), dynamic_radius)
        radial.setColorAt(0.0, QColor(255, 0, 0, 255))   # Rot nahe am Ball
        radial.setColorAt(1.0, QColor(255, 255, 0, 255)) # Gelb
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, size, size)
        
        # Berechne den Winkel vom Ball zur untersten Mitte des Spielfelds.
        bottom_center = QPointF(court_width/2, court_height)
        dx = bottom_center.x() - self.ball_x
        dy = bottom_center.y() - self.ball_y
        # Berechne den Winkel und negiere ihn, damit 0° am positiven x-Achse liegt und
        # die Richtung im Uhrzeigersinn (Qt-Konvention) gemessen wird.
        gradient_angle = (-math.degrees(math.atan2(dy, dx))) % 360
        
        # Konischer Gradient überlagern: Ausrichtung anhand des berechneten gradient_angle
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        conical = QConicalGradient(QPointF(size/2, size/2), gradient_angle)
        conical.setColorAt(0.0, QColor(255, 0, 0, 150))    # Rot bei Start (entspricht gradient_angle)
        conical.setColorAt(0.1, QColor(255, 255, 0, 0))      # Übergang transparent
        conical.setColorAt(0.9, QColor(255, 255, 0, 0))      # Übergang transparent
        conical.setColorAt(1.0, QColor(255, 0, 0, 150))    # Rot wieder
        painter.setBrush(QBrush(conical))
        painter.drawRect(0, 0, size, size)
        painter.end()
        
        # Setze eine halbtransparente Opacity (50 %) auf den kombinierten QPixmap
        temp = QPixmap(size, size)
        temp.fill(Qt.transparent)
        painter2 = QPainter(temp)
        painter2.setOpacity(0.5)
        painter2.drawPixmap(0, 0, combined)
        painter2.end()
        combined = temp
        
        # Richte den kombinierten Brush so aus, dass dessen Mittelpunkt dem Ballmittelpunkt entspricht.
        combined_brush = QBrush(combined)
        transform = QTransform()
        transform.translate(self.ball_x - size/2, self.ball_y - size/2)
        combined_brush.setTransform(transform)
        
        self.setBrush(combined_brush)
        self.setPen(QPen(Qt.NoPen))
