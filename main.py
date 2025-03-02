import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF  # Added QPointF import here

# Use absolute imports
from components.player_item import PlayerItem
from components.ball_item import BallItem
from sectors.attack_sector import AttackSector
from volleyball_field import VolleyballField, players
from utils import CourtDimensions

class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    # Court setup
    scale = 30  # 30 Pixel pro Meter
    volleyball_field = VolleyballField(scale)
    scene.addItem(volleyball_field)
    
    # Court dimensions
    court_dims = CourtDimensions(scale)
    
    # Set scene rectangle
    scene.setSceneRect(-volleyball_field.overhang, 0,
                       court_dims.width + 2*volleyball_field.overhang,
                       court_dims.height)
   
    # Ball
    ball_radius = 8
    ball_diameter = 2 * ball_radius
    ball_x = 4.5 * scale
    ball_y = 4.5 * scale
    ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dims)
    ball.setPos(ball_x - ball_radius, ball_y - ball_radius)
    ball.setBrush(QBrush(QColor("yellow")))
    ball.setPen(QPen(Qt.black, 2))
    ball.setZValue(500)  # High z-index but below players

    # Attack sector
    attack_sector = AttackSector(
        QPointF(ball_x, ball_y),
        court_width=court_dims.width,
        court_height=court_dims.height,
        net_y=court_dims.net_y
    )
    scene.addItem(attack_sector)
    ball.link_sector(attack_sector)

    # Defense team
    radius = 10
    diameter = 2 * radius
    defense_positions = [
        (4.5 * scale - radius, 15 * scale - radius),
        (2.5 * scale - radius, 15 * scale - radius),
        (6.5 * scale - radius, 15 * scale - radius),
        (4.5 * scale - radius, 16 * scale - radius),
        (2.5 * scale - radius, 16 * scale - radius),
        (6.5 * scale - radius, 16 * scale - radius),
    ]
    
    # Create players and add their components in the right order
    for i, (x, y) in enumerate(defense_positions):
        # New: Create player with rect originating at (0,0)
        player = PlayerItem(QRectF(0, 0, diameter, diameter), f"D{i+1}", ball, court_dims)
        # Set the actual position
        player.setPos(x, y)
        player.setBrush(QBrush(QColor("green")))
        
        # Initialize sectors
        player.init_sectors()

        # Add all sectors first (in reverse z-order)
        if "backward" in player.sectors:
            scene.addItem(player.sectors["backward"])
        if "wide" in player.sectors:
            scene.addItem(player.sectors["wide"])
        if "primary" in player.sectors:
            scene.addItem(player.sectors["primary"])
        
        # Add shadow
        scene.addItem(player.shadow)
        
        # Add player last (highest z-index)
        scene.addItem(player)
        
        # Add to global player list
        players.append(player)
    
    # Add ball to scene (after sectors but before players)
    scene.addItem(ball)
    
    # Create and show view
    view = ScalableGraphicsView(scene)
    view.setWindowTitle("Volleyball Angriffssituation")
    view.resize(1600, 1600)
    view.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
