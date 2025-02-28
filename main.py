import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF

# Importiere die ausgelagerten Klassen
from ball_item import BallItem, AttackSector
from player_item import PlayerItem
from core import players

# Zeichnet das Volleyballfeld (Vogelperspektive)
def drawCourt(scene):
    scale = 30
    court_width = 9 * scale
    court_length = 18 * scale
    scene.addRect(0, 0, court_width, court_length, QPen(Qt.black, 2))
    scene.addLine(0, court_length/2, court_width, court_length/2, QPen(Qt.black, 2))
    # Weitere Linien können hier hinzugefügt werden

class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    
    # Spielfeldabmessungen
    scale = 30  # 30 Pixel pro Meter
    court_dimensions = {"width": 9*scale, "height": 18*scale}
    
    drawCourt(scene)
    
    # Ball im oberen Spielfeldbereich
    ball_radius = 8
    ball_diameter = 2 * ball_radius
    ball_x = 4.5 * scale
    ball_y = 4.5 * scale  # obere Hälfte
    ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dimensions)
    ball.setPos(ball_x - ball_radius, ball_y - ball_radius)
    ball.setBrush(QBrush(QColor("yellow")))
    ball.setPen(QPen(Qt.black, 2))
    scene.addItem(ball)

    # Abwehrmannschaft
    radius = 15
    diameter = 2 * radius
    defense_positions = [
        (4.5 * scale - radius, 10 * scale - radius),
        (2.5 * scale - radius, 10 * scale - radius),
        (6.5 * scale - radius, 10 * scale - radius),
        (4.5 * scale - radius, 11 * scale - radius),
        (2.5 * scale - radius, 11 * scale - radius),
        (6.5 * scale - radius, 11 * scale - radius),
    ]
    
    for i, (x, y) in enumerate(defense_positions):
        player = PlayerItem(QRectF(x, y, diameter, diameter), f"D{i+1}", ball)
        player.setBrush(QBrush(QColor("green")))
        scene.addItem(player)
        scene.addItem(player.shadow)
        players.append(player)
        
    # Sektor (Angriffssituation) als eigenes Top-Level-Item
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
