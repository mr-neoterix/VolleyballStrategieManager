import sys
import math
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QWidget, QHBoxLayout, QGraphicsPathItem, QGraphicsLineItem
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF

# Verwende absolute Importe
from components.player_item import PlayerItem
from components.ball_item import BallItem
from sectors.attack_sector import AttackSector
from volleyball_field import VolleyballField, players
from utils_common import CourtDimensions
from defensive_positions_panel import DefensivePositionsPanel
from team_panel import TeamPanel  # Panel für Team-Speicherung/Ladung

# Import für Formation-Marker hinzufügen
from components.formation_marker_item import FormationMarkerItem

# Zusätzliche Importe - Direktimport statt utils.interpolation verwenden
from interpolation import interpolate_position, point_in_triangle  # Geänderter Import
from itertools import combinations

# Klasse für skalierbare Ansicht: passt Grafik an die Fenstergröße an
class ScalableGraphicsView(QGraphicsView):
    def resizeEvent(self, event):
        # Ansicht an den verfügbaren Bereich anpassen und Seitenverhältnis beibehalten
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

# Ermittelt die aktuelle Formation: Ballmittelpunkt, Spieleroffsets und definierte Annahmezonen
def getFormation():
    global ball, players
    ball_rect = ball.boundingRect()  # geändert von ball.rect()
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
    # Gibt ein Tupel zurück: (Ballmittelpunkt als (x,y), Offsets als (x,y)-Tupel-Liste, Zonenliste)
    ball_center_tuple = (ball_center.x(), ball_center.y())
    offsets_tuples = [(off.x(), off.y()) for off in offsets]
    return (ball_center_tuple, offsets_tuples, zones)

# Wendet eine gespeicherte defensive Formation an: positioniert Ball, Spieler und Annahmezonen
def apply_defensive_formation(formation):
    global ball, players
    # formation can be a tuple: (ball_center_tuple, offsets_list) or (ball_center_tuple, offsets_list, zones_list)
    if len(formation) == 3:
        saved_ball_center, offsets, zones = formation
    else:
        saved_ball_center, offsets = formation
        zones = []
    print("Anwende defensive Formation:", formation)
    ball_radius = ball.boundingRect().width() / 2  # geändert von ball.rect().width() / 2
    # Positioniere Ball so, dass sein Mittelpunkt saved_ball_center entspricht
    ball.setPos(saved_ball_center[0] - ball_radius, saved_ball_center[1] - ball_radius)
    ball.update_sector_position()
    
    # Für jeden Spieler Position aktualisieren und vorhandene Zonen löschen
    ball_center = QPointF(saved_ball_center[0], saved_ball_center[1])
    for i, player in enumerate(players):
        # Lösche alte Zonen
        if hasattr(player, 'clearZones'):
            player.clearZones()
        if i < len(offsets):
            offset = offsets[i]
            new_position = QPointF(ball_center.x() + offset[0], ball_center.y() + offset[1])
            player.setPos(new_position)
            # Spieler-Schatten/Sektoren aktualisieren
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

# Hauptfunktion: initialisiert GUI, Spielfeld, Ball, Spieler, Interpolation und Panels
def main():
    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    # Spielfeld-Einrichtung
    scale = 30  # 30 Pixel pro Meter
    volleyball_field = VolleyballField(scale)
    scene.addItem(volleyball_field)
    
    # Spielfeld-Abmessungen
    court_dims = CourtDimensions(scale)
    
    # Szene-Bereich festlegen
    scene.setSceneRect(-volleyball_field.overhang, 0,
                       court_dims.width + 2*volleyball_field.overhang,
                       court_dims.height)
   
    global ball  # deklariere Ball als globale Variable
    # Ball
    ball_radius = 12  # vergrößerter Ball-Radius
    ball_diameter = 2 * ball_radius
    ball_x = 4.5 * scale
    ball_y = 4.5 * scale
    ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dims)
    ball.setPos(ball_x - ball_radius, ball_y - ball_radius)
    ball.setZValue(500)  # Hoher Z-Index, aber unterhalb der Spieler

    # Angriffssektor
    attack_sector = AttackSector(
        QPointF(ball_x, ball_y),
        court_width=court_dims.width,
        court_height=court_dims.height,
        net_y=court_dims.net_y
    )
    scene.addItem(attack_sector)
    ball.link_sector(attack_sector)

    # Abwehrteam
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
    
    # Erstelle Spieler und weise Positionsnamen zu
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
        
        # Spieler zuletzt hinzufügen (höchster Z-Index)
        scene.addItem(player)
        
        # Spieler zur globalen Liste hinzufügen
        players.append(player)
    
    # Ball zur Szene hinzufügen (nach Sektoren, vor Spielern)
    scene.addItem(ball)
    
    # Erstelle QGraphicsView
    view = ScalableGraphicsView(scene)
    
    # Erstelle Haupt-Widget mit Ansicht und Abwehrpositionspanel
    main_widget = QWidget()
    main_layout = QHBoxLayout(main_widget)
    main_layout.addWidget(view)
    
    # Liste für Formation-Marker erstellen
    formation_markers = []
    
    # Struktur zur Speicherung von Dreiecken und Offsets für Interpolation
    interpolation_triangles = []
    interpolation_offsets = []
    
    # Globales Objekt zum Zeichnen des Interpolations-Dreiecks
    current_triangle_line = None
    
    def update_interpolation_data():
        # Aktualisiert Triangulationsdaten aus gespeicherten Formationen für Interpolation
        global ball
        interpolation_triangles.clear()
        interpolation_offsets.clear()
        
        # Mindestens 3 Formationen für Triangulation erforderlich
        if len(def_panel.formations) < 3:
            return
            
        # Erzeuge alle möglichen Dreiecke aus Ballpositionen
        ball_positions = [(form["ball"][0], form["ball"][1]) for form in def_panel.formations]
        player_offsets = [form["offsets"] for form in def_panel.formations]
        
        # Für jede Kombination von 3 Positionen ein Dreieck erstellen
        for indices in combinations(range(len(ball_positions)), 3):
            triangle = [ball_positions[i] for i in indices]
            triangle_offsets = [player_offsets[i] for i in indices]
            
            interpolation_triangles.append(triangle)
            interpolation_offsets.append(triangle_offsets)
    
    def interpolate_player_positions(x, y):
        # Interpoliert und aktualisiert Spielerpositionen basierend auf aktueller Ballposition
        nonlocal current_triangle_line  # erlaube Modifikation der äußeren Variable current_triangle_line
        """Try to interpolate player positions based on ball position"""
        # Zonen ausblenden, wenn Ball bewegt wird
        for player in players:
            player.clearZones()
        
        # Nur interpolieren, wenn genügend Formationen verfügbar sind
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
        
        # Gelbe Verbindungslinie für das ausgewählte Dreieck zeichnen oder entfernen
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
            path.lineTo(p1)  # Dreieck schließen
            pen = QPen(QColor("yellow"), 1)
            current_triangle_line = QGraphicsPathItem(path)
            current_triangle_line.setPen(pen)
            scene.addItem(current_triangle_line)
        else:
            if current_triangle_line is not None:
                scene.removeItem(current_triangle_line)
                current_triangle_line = None
        
        # Offsets wie zuvor interpolieren
        interpolated_offsets = interpolate_position(ball_pos, interpolation_triangles, interpolation_offsets)
        
        if interpolated_offsets:
            for i, player in enumerate(players):
                if i < len(interpolated_offsets):
                    offset = interpolated_offsets[i]
                    new_position = QPointF(x + offset[0], y + offset[1])
                    player.setPos(new_position)
                    player.updateShadow(x, y)
    
    def update_formation_markers(formations):
        # Aktualisiert visuelle Marker für jede gespeicherte defensive Formation
        # Alte Marker entfernen
        for marker in formation_markers:
            if marker.scene():
                scene.removeItem(marker)
        formation_markers.clear()
        
        # Neue Marker für jede Formation hinzufügen
        for i, form in enumerate(formations):
            ball_pos = form["ball"]
            marker = FormationMarkerItem(ball_pos, i)
            scene.addItem(marker)
            formation_markers.append(marker)
        
        # Nach Marker-Aktualisierung Interpolationsdaten aktualisieren
        update_interpolation_data()
    
    # Übergibt volleyball_field.scale als Skalierungsfaktor an das Panel
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
    
    # Initialisierung der Marker mit aktuell geladenen Formationen
    update_formation_markers(def_panel.formations)
    
    # Verknüpft Ballpositionsänderungen mit Interpolationsfunktion
    ball.positionChanged.connect(interpolate_player_positions)
    
    # Einrastfunktion: Überprüft Nähe des Balls zu gespeicherten Formationen und läd sie
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
