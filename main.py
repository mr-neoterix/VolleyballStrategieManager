import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QHBoxLayout, QWidget
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF

# Use absolute imports
from components.player_item import PlayerItem
from components.ball_item import BallItem
from components.defense_position_list import DefensePositionList
from sectors.attack_sector import AttackSector
from volleyball_field import VolleyballField, players
from utils import CourtDimensions

class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Volleyball Strategie Manager")
        self.setup_ui()
        
    def scene(self):
        return self.view.scene()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Spielfeld
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
        self.ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dims)
        self.ball.setPos(ball_x - ball_radius, ball_y - ball_radius)
        self.ball.setBrush(QBrush(QColor("yellow")))
        self.ball.setPen(QPen(Qt.black, 2))
        self.ball.setZValue(500)  # High z-index but below players
        self.ball.is_ball = True  # Markiere den Ball für die Erkennung
        
        # Attack sector
        attack_sector = AttackSector(
            QPointF(ball_x, ball_y),
            court_width=court_dims.width,
            court_height=court_dims.height,
            net_y=court_dims.net_y
        )
        scene.addItem(attack_sector)
        self.ball.link_sector(attack_sector)
        
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
            player = PlayerItem(QRectF(0, 0, diameter, diameter), f"D{i+1}", self.ball, court_dims)
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
        scene.addItem(self.ball)
        
        # Create and show view
        self.view = ScalableGraphicsView(scene)
        self.view.resize(1200, 1200)
        layout.addWidget(self.view)
        
        # Setze die PlayerItem-Klasse für die Erkennung
        self.player_class = PlayerItem
        
        # Liste der Stellungen
        self.position_list = DefensePositionList(self)
        self.position_list.player_class = self.player_class
        layout.addWidget(self.position_list)
        
        self.setLayout(layout)
        
        # Verbinde die Ball-Bewegung mit der Interpolation
        self.ball.mouseMoveEvent = self.ball_moved
    
    def ball_moved(self, event):
        # Rufe die ursprüngliche mouseMoveEvent-Methode auf
        BallItem.mouseMoveEvent(self.ball, event)
        
        # Hole die aktuelle Ballposition
        ball_rect = self.ball.rect()
        ball_center = self.ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
        
        # Aktualisiere die Koordinatenanzeige
        self.position_list.update_coord_label(ball_center.x(), ball_center.y())
        
        # Prüfe und interpoliere die Spielerpositionen
        self.position_list.check_and_interpolate(ball_center)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
