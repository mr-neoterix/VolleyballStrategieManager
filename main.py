import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QWidget, QHBoxLayout, QGraphicsPathItem  # added QGraphicsPathItem
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath  # Add import for drawing paths
from PyQt6.QtCore import Qt, QRectF, QPointF

# Use absolute imports
from components.player_item import PlayerItem
from components.ball_item import BallItem
from sectors.attack_sector import AttackSector
from volleyball_field import VolleyballField, players
from utils_common import CourtDimensions
from defensive_positions_panel import DefensivePositionsPanel

# Add import for the formation marker
from components.formation_marker_item import FormationMarkerItem

# Add new imports - use direct import instead of utils.interpolation
from interpolation import interpolate_position, point_in_triangle  # Modified import
from itertools import combinations

class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

def getFormation():
    global ball, players
    ball_rect = ball.boundingRect()  # changed from ball.rect()
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
    ball_radius = ball.boundingRect().width() / 2  # changed from ball.rect().width() / 2
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
    
    # Create a list to store formation markers
    formation_markers = []
    
    # Structure to store triangles and their offsets for interpolation
    interpolation_triangles = []
    interpolation_offsets = []
    
    # Global item for drawing the triangle connecting interpolation vertices
    current_triangle_line = None
    
    def update_interpolation_data():
        """Update the triangulation data based on saved formations"""
        global ball
        interpolation_triangles.clear()
        interpolation_offsets.clear()
        
        # Need at least 3 formations for triangulation
        if len(def_panel.formations) < 3:
            return
            
        # Generate all possible triangles from ball positions
        ball_positions = [(form["ball"][0], form["ball"][1]) for form in def_panel.formations]
        player_offsets = [form["offsets"] for form in def_panel.formations]
        
        # For each combination of 3 positions, create a triangle
        for indices in combinations(range(len(ball_positions)), 3):
            triangle = [ball_positions[i] for i in indices]
            triangle_offsets = [player_offsets[i] for i in indices]
            
            interpolation_triangles.append(triangle)
            interpolation_offsets.append(triangle_offsets)
    
    def interpolate_player_positions(x, y):
        """Try to interpolate player positions based on ball position"""
        nonlocal current_triangle_line  # add nonlocal declaration so we can modify it
        global players, ball
        
        # Only interpolate if we have enough formations
        if len(interpolation_triangles) == 0:
            return
            
        ball_pos = (x, y)
        
        # Select the smallest triangle (by area) that contains the current ball position
        selected_triangle = None
        min_area = None
        for triangle in interpolation_triangles:
            if point_in_triangle(ball_pos, *triangle):
                # Compute triangle area using the shoelace formula
                a, b, c = triangle
                area = abs(a[0]*(b[1]-c[1]) + b[0]*(c[1]-a[1]) + c[0]*(a[1]-b[1])) / 2
                if (min_area is None) or (area < min_area):
                    min_area = area
                    selected_triangle = triangle
        
        # Draw or clear the yellow connecting line for the selected triangle
        if selected_triangle:
            if current_triangle_line is not None:
                scene.removeItem(current_triangle_line)
            path = QPainterPath()
            p1 = QPointF(*selected_triangle[0])
            p2 = QPointF(*selected_triangle[1])
            p3 = QPointF(*selected_triangle[2])
            path.moveTo(p1)
            path.lineTo(p2)
            path.lineTo(p3)
            path.lineTo(p1)  # Close triangle
            pen = QPen(QColor("yellow"), 1)
            current_triangle_line = QGraphicsPathItem(path)
            current_triangle_line.setPen(pen)
            scene.addItem(current_triangle_line)
        else:
            if current_triangle_line is not None:
                scene.removeItem(current_triangle_line)
                current_triangle_line = None
        
        # Interpolate offsets as before
        interpolated_offsets = interpolate_position(ball_pos, interpolation_triangles, interpolation_offsets)
        
        if interpolated_offsets:
            for i, player in enumerate(players):
                if i < len(interpolated_offsets):
                    offset = interpolated_offsets[i]
                    new_position = QPointF(x + offset[0], y + offset[1])
                    player.setPos(new_position)
                    player.updateShadow(x, y)
    
    def update_formation_markers(formations):
        # Clear old markers
        for marker in formation_markers:
            if marker.scene():
                scene.removeItem(marker)
        formation_markers.clear()
        
        # Add new markers for each formation
        for i, form in enumerate(formations):
            ball_pos = form["ball"]
            marker = FormationMarkerItem(ball_pos, i)
            scene.addItem(marker)
            formation_markers.append(marker)
        
        # After updating markers, update interpolation data
        update_interpolation_data()
    
    # Pass volleyball_field.scale as scale_factor to the panel
    def_panel = DefensivePositionsPanel(get_formation_callback=getFormation, scale_factor=volleyball_field.scale)
    def_panel.formationSelected.connect(apply_defensive_formation)
    def_panel.formationsChanged.connect(update_formation_markers)
    main_layout.addWidget(def_panel)
    
    # Initialize markers with currently loaded formations
    update_formation_markers(def_panel.formations)
    
    # Connect ball position changes to interpolation function
    ball.positionChanged.connect(interpolate_player_positions)
    
    main_widget.setWindowTitle("Volleyball Angriffssituation")
    main_widget.resize(1600, 1600)
    main_widget.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
