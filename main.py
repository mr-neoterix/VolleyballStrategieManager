import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QWidget, QHBoxLayout
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF

# Use absolute imports
from components.player_item import PlayerItem
from components.ball_item import BallItem
from sectors.attack_sector import AttackSector
from volleyball_field import VolleyballField, players
from utils import CourtDimensions
from defensive_positions_panel import DefensivePositionsPanel

class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

def getFormation():
    global ball, players
    ball_rect = ball.rect()
    # Ball center in scene coordinates
    ball_center = ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
    offsets = []
    for player in players:
        offset = QPointF(player.scenePos().x() - ball_center.x(),
                         player.scenePos().y() - ball_center.y())
        offsets.append(offset)
    # Return a tuple: (ball_center as (x,y), list of offsets as (x,y) tuples)
    ball_center_tuple = (ball_center.x(), ball_center.y())
    offsets_tuples = [(off.x(), off.y()) for off in offsets]
    return (ball_center_tuple, offsets_tuples)

def apply_defensive_formation(formation):
    global ball, players
    # formation is a tuple: (ball_center_tuple, list_of_offsets)
    saved_ball_center = formation[0]
    offsets = formation[1]
    print("Anwenden defensive Stellung:", formation)
    ball_radius = ball.rect().width() / 2
    # Reposition ball so its center is at saved_ball_center
    ball.setPos(saved_ball_center[0] - ball_radius, saved_ball_center[1] - ball_radius)
    ball.update_sector_position()
    
    # For each player, update position using corresponding offset:
    ball_center = QPointF(saved_ball_center[0], saved_ball_center[1])
    for i, player in enumerate(players):
        if i < len(offsets):
            offset = offsets[i]
            new_position = QPointF(ball_center.x() + offset[0], ball_center.y() + offset[1])
            player.setPos(new_position)
            # Update player sectors/shadows using new ball center
            player.updateShadow(ball_center.x(), ball_center.y())

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
   
    global ball  # Declare ball as global here
    # Ball
    ball_radius = 8
    ball_diameter = 2 * ball_radius
    ball_x = 4.5 * scale
    ball_y = 4.5 * scale
    ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dims)
    ball.setPos(ball_x - ball_radius, ball_y - ball_radius)
    ball.setBrush(QBrush(QColor("yellow")))
    ball.setPen(QPen(QColor("black"), 2, Qt.PenStyle.SolidLine))
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
    
    # Create QGraphicsView
    view = ScalableGraphicsView(scene)
    
    # Create a main widget to hold both the view and the defensive positions panel
    main_widget = QWidget()
    main_layout = QHBoxLayout(main_widget)
    main_layout.addWidget(view)
    def_panel = DefensivePositionsPanel(get_formation_callback=getFormation)
    def_panel.formationSelected.connect(apply_defensive_formation)
    main_layout.addWidget(def_panel)
    
    main_widget.setWindowTitle("Volleyball Angriffssituation")
    main_widget.resize(1600, 1600)
    main_widget.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
