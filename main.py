import sys
import math
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QWidget, QHBoxLayout, QGraphicsPathItem, QGraphicsLineItem
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF

# Use absolute imports
from components.player_item import PlayerItem
from components.ball_item import BallItem
from sectors.attack_sector import AttackSector
from volleyball_field import VolleyballField, players
from utils_common import CourtDimensions
from defensive_positions_panel import DefensivePositionsPanel
from team_panel import TeamPanel  # Panel für Team-Speicherung/Ladung

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
    # Erfasse Annahmezonen für jeden Spieler
    zones = []
    for i, player in enumerate(players):
        # Prüfe ob Zone definiert ist
        if hasattr(player, 'zone_rect') and player.zone_rect is not None and player.zone_color is not None:
            r = player.zone_rect
            c = player.zone_color
            zones.append({
                'player_index': i,
                'rect': [r.x(), r.y(), r.width(), r.height()],
                'color': [c.red(), c.green(), c.blue(), c.alpha()]
            })
    # Return a tuple: (ball_center as (x,y), list of offsets as (x,y) tuples, list of zones)
    ball_center_tuple = (ball_center.x(), ball_center.y())
    offsets_tuples = [(off.x(), off.y()) for off in offsets]
    return (ball_center_tuple, offsets_tuples, zones)

def apply_defensive_formation(formation):
    global ball, players
    # formation can be a tuple: (ball_center_tuple, offsets_list) or (ball_center_tuple, offsets_list, zones_list)
    if len(formation) == 3:
        saved_ball_center, offsets, zones = formation
    else:
        saved_ball_center, offsets = formation
        zones = []
    print("Anwenden defensive Stellung:", formation)
    ball_radius = ball.boundingRect().width() / 2  # changed from ball.rect().width() / 2
    # Reposition ball so its center is at saved_ball_center
    ball.setPos(saved_ball_center[0] - ball_radius, saved_ball_center[1] - ball_radius)
    ball.update_sector_position()
    
    # For each player, update position and clear existing zones
    ball_center = QPointF(saved_ball_center[0], saved_ball_center[1])
    for i, player in enumerate(players):
        # Lösche alte Zonen
        if hasattr(player, 'clearZones'):
            player.clearZones()
        if i < len(offsets):
            offset = offsets[i]
            new_position = QPointF(ball_center.x() + offset[0], ball_center.y() + offset[1])
            player.setPos(new_position)
            # Update player sectors/shadows
            player.updateShadow(ball_center.x(), ball_center.y())
    # Nach der Aktualisierung: zeichne alle Annahmezonen
    for zone in zones:
        idx = zone.get('player_index')
        rect_vals = zone.get('rect', [])
        color_vals = zone.get('color', [])
        if idx is not None and idx < len(players) and len(rect_vals) == 4 and len(color_vals) == 4:
            r = QRectF(rect_vals[0], rect_vals[1], rect_vals[2], rect_vals[3])
            c = QColor(color_vals[0], color_vals[1], color_vals[2], color_vals[3])
            players[idx].addZone(r, c)

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
    ball_radius = 12  # vergrößerter Ball-Radius
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

    # Zeichne 3‑Meter‑Linien über Zonen (z=3)
    attack_line_y = volleyball_field.net_y - 3 * scale
    attack_line = QGraphicsLineItem(0, attack_line_y, court_dims.width, attack_line_y)
    pen_attack = QPen(QColor("red"), 2, Qt.PenStyle.DashLine)
    attack_line.setPen(pen_attack)
    attack_line.setZValue(50)
    scene.addItem(attack_line)
    defense_line_y = volleyball_field.net_y + 3 * scale
    defense_line = QGraphicsLineItem(0, defense_line_y, court_dims.width, defense_line_y)
    pen_def = QPen(QColor("red"), 2, Qt.PenStyle.DashLine)
    defense_line.setPen(pen_def)
    defense_line.setZValue(50)
    scene.addItem(defense_line)

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
    
    # Create players and add ihren Positionsnamen
    # Position-Namen für Spieler D1..D6: D1=MB, D2=OH, D3=S, D4=OH, D5=L, D6=Oppo
    position_names = ["MB", "OH", "S", "OH", "L", "Oppo"]
    for i, (x, y) in enumerate(defense_positions):
        # Spieler mit Position-Label
        label = position_names[i] if i < len(position_names) else ""
        player = PlayerItem(QRectF(0, 0, diameter, diameter), label, ball, court_dims)
        # Set the actual position
        player.setPos(x, y)
        player.setBrush(QBrush(QColor("green")))
        
        # (ActionSektoren entfernt) nur Schlagschatten und Spieler hinzufügen
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
        nonlocal current_triangle_line  # allow modifying outer current_triangle_line
        """Try to interpolate player positions based on ball position"""
        # Zonen ausblenden, wenn Ball bewegt wird
        for player in players:
            player.clearZones()
        
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
    
    # Zonen-Callback für alle Spieler setzen
    for idx, player in enumerate(players):
        player.player_index = idx
        player.zone_update_callback = def_panel.update_zone
    
    # TeamPanel rechts neben DefensivePositionsPanel
    # Callback zum Auslesen aktueller Spielernamen (unter dem Spieler)
    def get_player_names():
        return [player.name_label for player in players]

    # Funktion zur Anwendung eines geladenen Teams
    def on_team_selected(names):
        for i, player in enumerate(players):
            if i < len(names):
                player.name_label = names[i]
                player.name_text.setPlainText(names[i])
                player.updateNameTextPosition()

    team_panel = TeamPanel(get_names_callback=get_player_names)
    team_panel.teamSelected.connect(on_team_selected)
    main_layout.addWidget(team_panel)
    # Erst nach Verbindung des Signals initiales Team laden
    team_panel.load_teams()
    
    # Initialize markers with currently loaded formations
    update_formation_markers(def_panel.formations)
    
    # Connect ball position changes to interpolation function
    ball.positionChanged.connect(interpolate_player_positions)
    
    # Einrastfunktion: sobald Ball nahe einer gespeicherten Stellung ist
    def snap_to_formation(x, y):
        snap_radius = 10  # Pixelradius zum Einrasten (halbiert)
        # Suche nach nächster gespeicherter Formation
        for idx, form in enumerate(def_panel.formations):
            fx, fy = form["ball"]
            if math.hypot(x - fx, y - fy) <= snap_radius:
                saved = (fx, fy)
                offs = [tuple(off) for off in form.get("offsets", [])]
                zones = form.get("zones", [])
                # Lade Formation und setze Listenauswahl
                apply_defensive_formation((saved, offs, zones))
                def_panel.positions_list.setCurrentRow(idx)
                def_panel.on_item_clicked(def_panel.positions_list.currentItem())
                break
    ball.positionChanged.connect(snap_to_formation)
    
    main_widget.setWindowTitle("Volleyball Angriffssituation")
    main_widget.resize(1600, 1600)
    main_widget.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
