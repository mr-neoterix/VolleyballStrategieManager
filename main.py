import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF

# Importiere die ausgelagerten Klassen
from ball_item import BallItem, AttackSector
from player_item import PlayerItem
from core import players
from volleyball_field import VolleyballField

class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    # Spielfeld erstellen und hinzufügen (immer im Hintergrund)
    scale = 30  # 30 Pixel pro Meter
    volleyball_field = VolleyballField(scale)
    scene.addItem(volleyball_field)
    
    # Setze ein fixes Scene-Rechteck (z.B. exakt das Spielfeld, ggf. inkl. Überhang)
    scene.setSceneRect(-volleyball_field.overhang, 0,
                       volleyball_field.court_width + 2*volleyball_field.overhang,
                       volleyball_field.court_length)
   
    # court_dimensions für weitere Elemente
    court_dimensions = {"width": 9*scale, "height": 18*scale}
    
    # Ball
    ball_radius = 8
    ball_diameter = 2 * ball_radius
    ball_x = 4.5 * scale
    ball_y = 4.5 * scale
    ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dimensions)
    ball.setPos(ball_x - ball_radius, ball_y - ball_radius)
    ball.setBrush(QBrush(QColor("yellow")))
    ball.setPen(QPen(Qt.black, 2))

    # Abwehrmannschaft
    radius = 10
    diameter = 2 * radius
    defense_positions = [
        (4.5 * scale - radius, 10 * scale - radius),
        (2.5 * scale - radius, 10 * scale - radius),
        (6.5 * scale - radius, 10 * scale - radius),
        (4.5 * scale - radius, 11 * scale - radius),
        (2.5 * scale - radius, 11 * scale - radius),
        (6.5 * scale - radius, 11 * scale - radius),
    ]
    
    # Sektor (Angriffssituation) als eigenes Top-Level-Item
    attack_sector = AttackSector(ball_x, ball_y, radius=10 * scale)
    scene.addItem(attack_sector)
    ball.link_sector(attack_sector)
    
    for i, (x, y) in enumerate(defense_positions):
        player = PlayerItem(QRectF(x, y, diameter, diameter), f"D{i+1}", ball)
        player.setBrush(QBrush(QColor("green")))
        
        # Initialisiere Aktionssektoren und füge beide zur Szene hinzu
        player.init_action_sector()
        
        # Füge den breiten Sektor zuerst hinzu (niedrigerer z-Index)
        if player.wide_action_sector:
            scene.addItem(player.wide_action_sector)
            
        # Dann den schmalen Sektor
        if player.action_sector:
            scene.addItem(player.action_sector)
        
        # Füge Schlagschatten hinzu
        scene.addItem(player.shadow)
        
        # Füge Spieler zur Szene hinzu (nach Schatten und Aktionssektor)
        scene.addItem(player)
        
        # Füge Spieler zur globalen Liste hinzu
        players.append(player)
        
    # Füge den Ball nach den Spielern hinzu (erscheint über dem Spielfeld, aber unter den Spielern)
    ball.setZValue(500)  # Höher als das Spielfeld, aber niedriger als die Spieler
    scene.addItem(ball)
    
    view = ScalableGraphicsView(scene)
    view.setWindowTitle("Volleyball Angriffssituation")
    view.resize(1600, 1600)
    view.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
