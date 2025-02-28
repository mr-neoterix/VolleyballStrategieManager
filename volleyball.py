import sys
import math
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPathItem
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath, QRadialGradient, QConicalGradient
from PyQt5.QtCore import Qt, QRectF, QPointF

# Klasse für bewegliche (draggable) Kreise
class DraggableEllipse(QGraphicsEllipseItem):
    def __init__(self, rect, label=""):
        super().__init__(rect)
        # Flags setzen, damit der Artikel mit der Maus bewegt werden kann
        self.setFlags(QGraphicsEllipseItem.ItemIsSelectable | QGraphicsEllipseItem.ItemIsMovable)
        # Standardfarbe (kann später überschrieben werden)
        self.setBrush(QBrush(QColor("blue")))
        self.setPen(QPen(Qt.black, 2))
        # Beschriftung hinzufügen
        if label:
            text = QGraphicsTextItem(label, self)
            text.setDefaultTextColor(Qt.white)
            # Zentriere die Beschriftung innerhalb des Kreises
            text.setPos(rect.x() + rect.width()/2 - text.boundingRect().width()/2,
                        rect.y() + rect.height()/2 - text.boundingRect().height()/2)

# Klasse für statische Kreise (Blockspieler)
class StaticEllipse(QGraphicsEllipseItem):
    def __init__(self, rect, label=""):
        super().__init__(rect)
        self.setBrush(QBrush(QColor("red")))
        self.setPen(QPen(Qt.black, 2))
        if label:
            text = QGraphicsTextItem(label, self)
            text.setDefaultTextColor(Qt.white)
            text.setPos(rect.x() + rect.width()/2 - text.boundingRect().width()/2,
                        rect.y() + rect.height()/2 - text.boundingRect().height()/2)

# Neue Klasse für den Schlagsektor (Winkelbereich der möglichen Schlagrichtungen)
class AttackSector(QGraphicsPathItem):
    def __init__(self, ball_x, ball_y, radius=300):
        super().__init__()
        self.ball_x = ball_x
        self.ball_y = ball_y
        self.radius = radius  # Wird nun überschrieben
        self.draw_sector()
        
    def updatePosition(self, ball_x, ball_y):
        # Absolute Szenenkoordinaten werden übernommen
        self.ball_x = ball_x
        self.ball_y = ball_y
        self.draw_sector()
        
    def draw_sector(self):
        path = QPainterPath()
        # Spielfeldparameter (scale=30)
        court_width = 9 * 30
        net_y = 270  # Untere Grenze des Angriffsbereichs (Netz)
        left_net = QPointF(0, net_y)
        right_net = QPointF(court_width, net_y)
        
        # Dynamischer Radius: Abstand vom Ballmittelpunkt zum unteren Spielfeldrand (net_y * 2)
        dynamic_radius = net_y * 2 - self.ball_y
        
        # Berechne Winkel basierend auf den Netzkanten und dem Ballmittelpunkt.
        angle_left = math.degrees(math.atan2(self.ball_y - left_net.y(), left_net.x() - self.ball_x))
        angle_right = math.degrees(math.atan2(self.ball_y - right_net.y(), right_net.x() - self.ball_x))
        
        # Zum Zeichnen: Starte beim linken Winkel und zeichne bis zum rechten Winkel.
        start_angle = angle_left
        sweep_angle = angle_right - angle_left
        
        # Zeichne den Bogen des Sektors:
        path.moveTo(self.ball_x, self.ball_y)
        path.arcTo(self.ball_x - dynamic_radius, self.ball_y - dynamic_radius,
                   dynamic_radius * 2, dynamic_radius * 2,
                   start_angle, sweep_angle)
        path.lineTo(self.ball_x, self.ball_y)
        self.setPath(path)
        
        # Erstelle ein QPixmap, um beide Gradienten zu kombinieren.
        from PyQt5.QtGui import QPixmap, QPainter, QTransform
        size = int(dynamic_radius * 2)
        combined = QPixmap(size, size)
        combined.fill(Qt.transparent)
        
        painter = QPainter(combined)
        # Zeichne den radialen Gradient zuerst.
        radial = QRadialGradient(QPointF(size/2, size/2), dynamic_radius)
        radial.setColorAt(0.0, QColor(255, 0, 0, 255))   # Rot nahe am Ball
        radial.setColorAt(1.0, QColor(255, 255, 0, 255)) # Gelb
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, size, size)
        
        # Jetzt den konischen Gradient überlagern.
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        conical = QConicalGradient(QPointF(size/2, size/2), 270)
        conical.setColorAt(0.0, QColor(255, 0, 0, 150))    # Rot bei 270°
        conical.setColorAt(0.1, QColor(255, 255, 0, 0)) # Gelb bei (270+90=360°)
        conical.setColorAt(0.9, QColor(255, 255, 0, 0)) # Gelb bei (270-90=180°)
        conical.setColorAt(1.0, QColor(255, 0, 0, 150))    # Rot bei 270°
        painter.setBrush(QBrush(conical))
        painter.drawRect(0, 0, size, size)
        painter.end()
        
        # ... nach painter.end() statt der Pixeliteration:
        temp = QPixmap(size, size)
        temp.fill(Qt.transparent)
        painter2 = QPainter(temp)
        painter2.setOpacity(0.5)  # Setze die Opacity auf 50 %
        painter2.drawPixmap(0, 0, combined)
        painter2.end()
        combined = temp

        # Stelle sicher, dass die Mitte des QPixmaps mit dem Ballmittelpunkt übereinstimmt.
        combined_brush = QBrush(combined)
        transform = QTransform()
        transform.translate(self.ball_x - size/2, self.ball_y - size/2)
        combined_brush.setTransform(transform)

        self.setBrush(combined_brush)
        self.setPen(QPen(Qt.black, 2))

# Neue Klasse für den Ball, der seinen eigenen Sektor aktualisiert
class BallItem(DraggableEllipse):
    def __init__(self, rect, sector=None, label="", court_dimensions=None):
        super().__init__(rect, label)
        self.sector = sector
        # Spielfeldabmessungen: Diese beziehen sich auf das originale Spielfeld
        self.court_dimensions = court_dimensions or {"width": 9*30, "height": 18*30}
        self.half_court = self.court_dimensions["height"] / 2

    def link_sector(self, sector):
        self.sector = sector
        self.update_sector_position()

    def update_sector_position(self):
        """Berechnet den Ballmittelpunkt absolut in der Szene und gibt diesen an den Sektor weiter"""
        if self.sector:
            # Berechnung: scenePos() (obere linke Ecke) + (Breite/2, Höhe/2)
            ball_rect = self.rect()
            center = self.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
            self.sector.updatePosition(center.x(), center.y())

    def mouseMoveEvent(self, event):
        # Standard-Drag-Verhalten: hier ändert bereits QGraphicsEllipseItem seine Position
        super().mouseMoveEvent(event)

        ball_rect = self.rect()
        current_pos = self.scenePos()  # Oberer linker Punkt in Szenenkoordinaten
        # Berechne den Ballmittelpunkt anhand der aktuellen Position
        ball_center = current_pos + QPointF(ball_rect.width()/2, ball_rect.height()/2)

        new_pos = QPointF(current_pos)
        needs_update = False

        # Linke Grenze: Die obere linke Ecke darf nicht links von 0 liegen.
        if current_pos.x() < 0:
            new_pos.setX(0)
            needs_update = True

        # Rechte Grenze: Der rechte Rand (x + Breite) darf nicht über court_width hinaus.
        if current_pos.x() + ball_rect.width() > self.court_dimensions["width"]:
            new_pos.setX(self.court_dimensions["width"] - ball_rect.width())
            needs_update = True

        # Obere Grenze: Der obere Rand darf nicht oberhalb von 0 liegen.
        if current_pos.y() < 0:
            new_pos.setY(0)
            needs_update = True

        # Untere Grenze: Die Unterkante darf nicht unterhalb der Mittellinie (half_court) liegen.
        if current_pos.y() + ball_rect.height() > self.half_court:
            new_pos.setY(self.half_court - ball_rect.height())
            needs_update = True

        if needs_update:
            self.setPos(new_pos)

        # Nach Korrektur den Ballmittelpunkt aktualisieren und den Sektor neu positionieren.
        self.update_sector_position()

# Zeichnet das Volleyballfeld (Vogelperspektive)
def drawCourt(scene):
    # Mit einem Skalierungsfaktor von 30 Pixel pro Meter ergibt sich:
    scale = 30
    court_width = 9 * scale
    court_length = 18 * scale

    # Zeichne das Spielfeld (einfaches Rechteck)
    scene.addRect(0, 0, court_width, court_length, QPen(Qt.black, 2))
    # Mittellinie (Netzlinie)
    scene.addLine(0, court_length/2, court_width, court_length/2, QPen(Qt.black, 2))
    # Weitere Linien können hier hinzugefügt werden

class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    # Definiere Spielfeldabmessungen
    scale = 30  # Skalierungsfaktor: 30 Pixel pro Meter
    court_dimensions = {"width": 9*scale, "height": 18*scale}

    # Zeichne das Spielfeld
    drawCourt(scene)

    radius = 15
    diameter = 2 * radius

    # Positionierung der Abwehrmannschaft (bewegliche, grüne Kreise)
    defense_positions = [
        (4.5 * scale - radius, 10 * scale - radius),
        (2.5 * scale - radius, 10 * scale - radius),
        (6.5 * scale - radius, 10 * scale - radius),
        (4.5 * scale - radius, 11 * scale - radius),
        (2.5 * scale - radius, 11 * scale - radius),
        (6.5 * scale - radius, 11 * scale - radius),
    ]
    for i, (x, y) in enumerate(defense_positions):
        player = DraggableEllipse(QRectF(x, y, diameter, diameter), f"D{i+1}")
        player.setBrush(QBrush(QColor("green")))
        scene.addItem(player)

    # Positioniere den Ball im oberen Spielfeldbereich
    ball_radius = 8
    ball_diameter = 2 * ball_radius
    ball_x = 4.5 * scale
    ball_y = 4.5 * scale  # Oberer Bereich: obere Hälfte

    # Wichtig: Setze die Position des BallItems explizit – so ist scenePos() korrekt!
    ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dimensions)
    ball.setPos(ball_x - ball_radius, ball_y - ball_radius)
    ball.setBrush(QBrush(QColor("yellow")))
    ball.setPen(QPen(Qt.black, 2))
    scene.addItem(ball)

    # Falls Du den Sektor nutzen möchtest, füge ihn als separates Top-Level-Item hinzu:
    attack_sector = AttackSector(ball_x, ball_y, radius=10 * scale)
    scene.addItem(attack_sector)
    ball.link_sector(attack_sector)

    view = ScalableGraphicsView(scene)
    view.setWindowTitle("Volleyball Angriffssituation")
    view.resize(1600, 1600)
    view.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
