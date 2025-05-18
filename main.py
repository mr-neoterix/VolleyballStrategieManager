import sys  # Importiert das sys-Modul für den Zugriff auf Systemparameter und -funktionen.
import math  # Importiert das math-Modul für mathematische Operationen.
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QWidget, QHBoxLayout, QGraphicsPathItem, QGraphicsLineItem  # Importiert notwendige Widgets von PyQt6.
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath  # Importiert Klassen für Pinsel, Stifte, Farben und Pfade von PyQt6.
from PyQt6.QtCore import Qt, QRectF, QPointF  # Importiert Kernfunktionalitäten und Typen wie Qt-Konstanten, QRectF und QPointF.

# Verwende absolute Importe
from components.player_item import PlayerItem  # Importiert die PlayerItem-Klasse aus dem components-Modul.
from components.ball_item import BallItem  # Importiert die BallItem-Klasse aus dem components-Modul.
from sectors.attack_sector import AttackSector  # Importiert die AttackSector-Klasse aus dem sectors-Modul.
from volleyball_field import VolleyballField, players  # Importiert VolleyballField und die globale Spielerliste.
from utils import CourtDimensions  # Importiert CourtDimensions für Spielfeldabmessungen aus utils.py.
from defensive_positions_panel import DefensivePositionsPanel  # Importiert das Panel für Defensivpositionen.
from team_panel import TeamPanel  # Importiert das Panel für Team-Speicherung/Ladung.

# Import für Formation-Marker hinzufügen
from components.formation_marker_item import FormationMarkerItem  # Importiert die Klasse für Formationsmarker.

# Zusätzliche Importe - Direktimport statt utils.interpolation verwenden
from interpolation import interpolate_position, point_in_triangle  # Importiert Interpolationsfunktionen direkt.
from itertools import combinations  # Importiert combinations für die Erzeugung von Dreieckskombinationen.

# Klasse für skalierbare Ansicht: passt Grafik an die Fenstergröße an
class ScalableGraphicsView(QGraphicsView):  # Definiert eine von QGraphicsView abgeleitete Klasse für eine skalierbare Ansicht.
    def resizeEvent(self, event):  # Überschreibt das resizeEvent, um die Ansicht bei Größenänderung anzupassen.
        # Ansicht an den verfügbaren Bereich anpassen und Seitenverhältnis beibehalten
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)  # Passt den Inhalt der Szene unter Beibehaltung des Seitenverhältnisses in die Ansicht ein.
        super().resizeEvent(event)  # Ruft das resizeEvent der Basisklasse auf.

# Ermittelt die aktuelle Formation: Ballmittelpunkt, Spieleroffsets und definierte Annahmezonen
def getFormation():  # Definiert eine Funktion, um die aktuelle Formation (Ball, Spielerpositionen, Zonen) zu ermitteln.
    global ball, players  # Deklariert, dass die globalen Variablen ball und players verwendet werden.
    ball_rect = ball.boundingRect()  # Holt das Bounding-Rechteck des Balls (geändert von ball.rect()).
    # Ballmittelpunkt in Szenenkoordinaten
    ball_center = ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)  # Berechnet den Mittelpunkt des Balls in Szenenkoordinaten.
    offsets = []  # Initialisiert eine leere Liste für die Spieler-Offsets.
    for player in players:  # Iteriert über alle Spieler.
        offset = QPointF(player.scenePos().x() - ball_center.x(),  # Berechnet den x-Offset des Spielers relativ zum Ball.
                         player.scenePos().y() - ball_center.y())  # Berechnet den y-Offset des Spielers relativ zum Ball.
        offsets.append(offset)  # Fügt den Offset zur Liste hinzu.
    # Erfasse Annahmezonen für jeden Spieler
    zones = []  # Initialisiert eine leere Liste für die Annahmezonen.
    for i, player in enumerate(players):  # Iteriert über alle Spieler mit ihrem Index.
        # Prüfe ob Zone definiert ist
        if hasattr(player, 'zone_rect') and player.zone_rect is not None and player.zone_color is not None:  # Überprüft, ob der Spieler eine definierte Annahmezone hat.
            r = player.zone_rect  # Holt das Rechteck der Zone.
            c = player.zone_color  # Holt die Farbe der Zone.
            zones.append({  # Fügt die Zonendaten als Dictionary zur Liste hinzu.
                'player_index': i,  # Speichert den Spielerindex.
                'rect': [r.x(), r.y(), r.width(), r.height()],  # Speichert die Rechteckkoordinaten.
                'color': [c.red(), c.green(), c.blue(), c.alpha()]  # Speichert die Farbwerte.
            })
    # Gibt ein Tupel zurück: (Ballmittelpunkt als (x,y), Offsets als (x,y)-Tupel-Liste, Zonenliste)
    ball_center_tuple = (ball_center.x(), ball_center.y())  # Konvertiert den Ballmittelpunkt in ein Tupel.
    offsets_tuples = [(off.x(), off.y()) for off in offsets]  # Konvertiert die Offsets in eine Liste von Tupeln.
    return (ball_center_tuple, offsets_tuples, zones)  # Gibt die vollständigen Formationsdaten zurück.

# Wendet eine gespeicherte defensive Formation an: positioniert Ball, Spieler und Annahmezonen
def apply_defensive_formation(formation):  # Definiert eine Funktion, um eine gespeicherte Formation anzuwenden.
    global ball, players  # Deklariert die Verwendung der globalen Variablen ball und players.
    # formation kann ein Tupel sein: (ball_center_tuple, offsets_list) oder (ball_center_tuple, offsets_list, zones_list)
    if len(formation) == 3:  # Überprüft, ob Zonendaten in der Formation enthalten sind.
        saved_ball_center, offsets, zones = formation  # Entpackt die Formation mit Zonen.
    else:  # Falls keine Zonendaten vorhanden sind.
        saved_ball_center, offsets = formation  # Entpackt die Formation ohne Zonen.
        zones = []  # Initialisiert eine leere Zonenliste.
    print("Anwende defensive Formation:", formation)  # Gibt eine Debug-Meldung aus.
    ball_radius = ball.boundingRect().width() / 2  # Holt den Ballradius (geändert von ball.rect().width() / 2).
    # Positioniere Ball so, dass sein Mittelpunkt saved_ball_center entspricht
    ball.setPos(saved_ball_center[0] - ball_radius, saved_ball_center[1] - ball_radius)  # Setzt die Position des Balls basierend auf dem gespeicherten Mittelpunkt.
    ball.update_sector_position()  # Aktualisiert die Position des zugehörigen Sektors.
    
    # Für jeden Spieler Position aktualisieren und vorhandene Zonen löschen
    ball_center = QPointF(saved_ball_center[0], saved_ball_center[1])  # Erstellt ein QPointF-Objekt für den Ballmittelpunkt.
    for i, player in enumerate(players):  # Iteriert über alle Spieler mit ihrem Index.
        # Lösche alte Zonen
        if hasattr(player, 'clearZones'):  # Überprüft, ob der Spieler eine Methode zum Löschen von Zonen hat.
            player.clearZones()  # Ruft die Methode zum Löschen der Zonen des Spielers auf.
        if i < len(offsets):  # Überprüft, ob für diesen Spieler ein Offset vorhanden ist.
            offset = offsets[i]  # Holt den Offset für den aktuellen Spieler.
            new_position = QPointF(ball_center.x() + offset[0], ball_center.y() + offset[1])  # Berechnet die neue Spielerposition.
            player.setPos(new_position)  # Setzt die neue Position des Spielers.
            # Spieler-Schatten/Sektoren aktualisieren
            player.updateShadow(ball_center.x(), ball_center.y())  # Aktualisiert den Schatten des Spielers basierend auf der Ballposition.
    # Nach der Aktualisierung: zeichne alle Annahmezonen
    for zone in zones:  # Iteriert über alle Zonen in der Formation.
        idx = zone.get('player_index')  # Holt den Spielerindex für die Zone.
        rect_vals = zone.get('rect', [])  # Holt die Rechteckwerte, Standard ist eine leere Liste.
        color_vals = zone.get('color', [])  # Holt die Farbwerte, Standard ist eine leere Liste.
        if idx is not None and idx < len(players) and len(rect_vals) == 4 and len(color_vals) == 4:  # Überprüft die Gültigkeit der Zonendaten.
            r = QRectF(rect_vals[0], rect_vals[1], rect_vals[2], rect_vals[3])  # Erstellt ein QRectF-Objekt für die Zone.
            c = QColor(color_vals[0], color_vals[1], color_vals[2], color_vals[3])  # Erstellt ein QColor-Objekt für die Zone.
            players[idx].addZone(r, c)  # Fügt die Zone dem entsprechenden Spieler hinzu.

# Hauptfunktion: initialisiert GUI, Spielfeld, Ball, Spieler, Interpolation und Panels
def main():  # Definiert die Hauptfunktion der Anwendung.
    app = QApplication(sys.argv)  # Erstellt eine QApplication-Instanz.
    scene = QGraphicsScene()  # Erstellt eine QGraphicsScene-Instanz.

    # Spielfeld-Einrichtung
    scale = 30  # Definiert den Maßstab: 30 Pixel pro Meter.
    volleyball_field = VolleyballField(scale)  # Erstellt eine Instanz des Volleyballfeldes.
    scene.addItem(volleyball_field)  # Fügt das Volleyballfeld zur Szene hinzu.
    
    # Spielfeld-Abmessungen
    court_dims = CourtDimensions(scale)  # Erstellt eine Instanz von CourtDimensions.
    
    # Szene-Bereich festlegen
    scene.setSceneRect(-volleyball_field.overhang, 0,  # Setzt das Rechteck der Szene.
                       court_dims.width + 2*volleyball_field.overhang,  # Breite der Szene.
                       court_dims.height)  # Höhe der Szene.
   
    global ball  # Deklariert ball als globale Variable.
    # Ball
    ball_radius = 12  # Definiert den Radius des Balls (vergrößert für bessere Sichtbarkeit).
    ball_diameter = 2 * ball_radius  # Berechnet den Durchmesser des Balls.
    ball_x = 4.5 * scale  # Setzt die initiale x-Position des Balls.
    ball_y = 4.5 * scale  # Setzt die initiale y-Position des Balls.
    ball = BallItem(QRectF(0, 0, ball_diameter, ball_diameter), label="", court_dimensions=court_dims)  # Erstellt eine BallItem-Instanz.
    ball.setPos(ball_x - ball_radius, ball_y - ball_radius)  # Setzt die Position des Balls (linke obere Ecke).
    ball.setZValue(500)  # Setzt den Z-Wert des Balls, um ihn über anderen Elementen darzustellen.

    # Angriffssektor
    attack_sector = AttackSector(  # Erstellt eine Instanz des Angriffssektors.
        QPointF(ball_x, ball_y),  # Setzt den Mittelpunkt des Sektors.
        court_width=court_dims.width,  # Übergibt die Breite des Spielfelds.
        court_height=court_dims.height,  # Übergibt die Höhe des Spielfelds.
        net_y=court_dims.net_y  # Übergibt die y-Position des Netzes.
    )
    scene.addItem(attack_sector)  # Fügt den Angriffssektor zur Szene hinzu.
    ball.link_sector(attack_sector)  # Verknüpft den Ball mit dem Angriffssektor.

    # Abwehrteam
    radius = 10  # Definiert den Radius der Spieler.
    diameter = 2 * radius  # Berechnet den Durchmesser der Spieler.
    defense_positions = [  # Definiert die initialen Positionen der Abwehrspieler.
        (4.5 * scale - radius, 15 * scale - radius),
        (2.5 * scale - radius, 15 * scale - radius),
        (6.5 * scale - radius, 15 * scale - radius),
        (4.5 * scale - radius, 16 * scale - radius),
        (2.5 * scale - radius, 16 * scale - radius),
        (6.5 * scale - radius, 16 * scale - radius),
    ]
    
    # Erstelle Spieler und weise Positionsnamen zu
    # Positionsnamen für Spieler D1..D6: D1=MB, D2=OH, D3=S, D4=OH, D5=L, D6=Oppo
    position_names = ["MB", "OH", "S", "OH", "L", "Oppo"]  # Definiert die Positionsnamen für die Spieler.
    for i, (x, y) in enumerate(defense_positions):  # Iteriert über die Verteidigungspositionen.
        # Spieler mit Positions-Label
        label = position_names[i] if i < len(position_names) else ""  # Holt den Positionsnamen oder einen leeren String.
        player = PlayerItem(QRectF(0, 0, diameter, diameter), label, ball, court_dims)  # Erstellt eine PlayerItem-Instanz.
        # Setzt die aktuelle Position
        player.setPos(x, y)  # Setzt die Position des Spielers.
        player.setBrush(QBrush(QColor("green")))  # Setzt die Farbe des Spielers auf Grün.
        
        # (ActionSektoren entfernt) nur Schlagschatten und Spieler hinzufügen
        scene.addItem(player.shadow)  # Fügt den Schatten des Spielers zur Szene hinzu.
        
        # Spieler zuletzt hinzufügen (höchster Z-Index)
        scene.addItem(player)  # Fügt den Spieler zur Szene hinzu (über dem Schatten).
        
        # Spieler zur globalen Liste hinzufügen
        players.append(player)  # Fügt den Spieler zur globalen Spielerliste hinzu.
    
    # Ball zur Szene hinzufügen (nach Sektoren, vor Spielern)
    scene.addItem(ball)  # Fügt den Ball zur Szene hinzu.
    
    # Erstelle QGraphicsView
    view = ScalableGraphicsView(scene)  # Erstellt eine Instanz der skalierbaren Ansicht.
    
    # Erstelle Haupt-Widget mit Ansicht und Abwehrpositionspanel
    main_widget = QWidget()  # Erstellt das Haupt-Widget.
    main_layout = QHBoxLayout(main_widget)  # Erstellt ein horizontales Layout für das Haupt-Widget.
    main_layout.addWidget(view)  # Fügt die Ansicht zum Layout hinzu.
    
    # Liste für Formation-Marker erstellen
    formation_markers = []  # Initialisiert eine leere Liste für Formationsmarker.
    
    # Struktur zur Speicherung von Dreiecken und Offsets für Interpolation
    interpolation_triangles = []  # Initialisiert eine leere Liste für Interpolationsdreiecke.
    interpolation_offsets = []  # Initialisiert eine leere Liste für Interpolations-Offsets.
    
    # Globales Objekt zum Zeichnen des Interpolations-Dreiecks
    current_triangle_line = None  # Initialisiert eine Variable für die Linie des aktuellen Interpolationsdreiecks.
    
    def update_interpolation_data():  # Definiert eine Funktion zur Aktualisierung der Interpolationsdaten.
        # Aktualisiert Triangulationsdaten aus gespeicherten Formationen für Interpolation
        global ball  # Deklariert die Verwendung der globalen Variable ball.
        interpolation_triangles.clear()  # Leert die Liste der Interpolationsdreiecke.
        interpolation_offsets.clear()  # Leert die Liste der Interpolations-Offsets.
        
        # Mindestens 3 Formationen für Triangulation erforderlich
        if len(def_panel.formations) < 3:  # Überprüft, ob genügend Formationen für die Triangulation vorhanden sind.
            return  # Bricht ab, wenn nicht genügend Formationen vorhanden sind.
            
        # Erzeuge alle möglichen Dreiecke aus Ballpositionen
        ball_positions = [(form["ball"][0], form["ball"][1]) for form in def_panel.formations]  # Extrahiert die Ballpositionen aus den gespeicherten Formationen.
        player_offsets = [form["offsets"] for form in def_panel.formations]  # Extrahiert die Spieler-Offsets aus den gespeicherten Formationen.
        
        # Für jede Kombination von 3 Positionen ein Dreieck erstellen
        for indices in combinations(range(len(ball_positions)), 3):  # Iteriert über alle Kombinationen von 3 Indizes.
            triangle = [ball_positions[i] for i in indices]  # Erstellt ein Dreieck aus den entsprechenden Ballpositionen.
            triangle_offsets = [player_offsets[i] for i in indices]  # Holt die entsprechenden Spieler-Offsets.
            
            interpolation_triangles.append(triangle)  # Fügt das Dreieck zur Liste hinzu.
            interpolation_offsets.append(triangle_offsets)  # Fügt die Offsets zur Liste hinzu.
    
    def interpolate_player_positions(x, y):  # Definiert eine Funktion zur Interpolation der Spielerpositionen.
        # Interpoliert und aktualisiert Spielerpositionen basierend auf aktueller Ballposition
        nonlocal current_triangle_line  # Erlaubt die Modifikation der äußeren Variable current_triangle_line.
        """Versucht, Spielerpositionen basierend auf der Ballposition zu interpolieren.""" # Englischer Kommentar übersetzt.
        # Zonen ausblenden, wenn Ball bewegt wird
        for player in players:  # Iteriert über alle Spieler.
            player.clearZones()  # Löscht die Annahmezonen der Spieler.
        
        # Nur interpolieren, wenn genügend Formationen verfügbar sind
        if len(interpolation_triangles) == 0:  # Überprüft, ob Interpolationsdreiecke vorhanden sind.
            return  # Bricht ab, wenn keine Dreiecke vorhanden sind.
            
        ball_pos = (x, y)  # Speichert die aktuelle Ballposition als Tupel.
        
        # Wähle das kleinste Dreieck (nach Fläche), das die aktuelle Ballposition enthält
        selected_triangle = None  # Initialisiert das ausgewählte Dreieck mit None.
        min_area = None  # Initialisiert die minimale Fläche mit None.
        for triangle in interpolation_triangles:  # Iteriert über alle Interpolationsdreiecke.
            if point_in_triangle(ball_pos, *triangle):  # Überprüft, ob der Ball im aktuellen Dreieck liegt.
                # Berechne die Dreiecksfläche mit der Shoelace-Formel
                a, b, c = triangle  # Entpackt die Eckpunkte des Dreiecks.
                area = abs(a[0]*(b[1]-c[1]) + b[0]*(c[1]-a[1]) + c[0]*(a[1]-b[1])) / 2  # Berechnet die Fläche des Dreiecks.
                if (min_area is None) or (area < min_area):  # Überprüft, ob dies das kleinste Dreieck ist, das den Punkt enthält.
                    min_area = area  # Aktualisiert die minimale Fläche.
                    selected_triangle = triangle  # Setzt das aktuell kleinste Dreieck.
        
        # Gelbe Verbindungslinie für das ausgewählte Dreieck zeichnen oder entfernen
        if selected_triangle:  # Wenn ein Dreieck ausgewählt wurde.
            if current_triangle_line is not None:  # Wenn bereits eine Linie gezeichnet wurde.
                scene.removeItem(current_triangle_line)  # Entfernt die alte Linie.
            path = QPainterPath()  # Erstellt einen neuen QPainterPath.
            p1 = QPointF(*selected_triangle[0])  # Erster Punkt des Dreiecks.
            p2 = QPointF(*selected_triangle[1])  # Zweiter Punkt des Dreiecks.
            p3 = QPointF(*selected_triangle[2])  # Dritter Punkt des Dreiecks.
            path.moveTo(p1)  # Bewegt den Pfad zum ersten Punkt.
            path.lineTo(p2)  # Zeichnet eine Linie zum zweiten Punkt.
            path.lineTo(p3)  # Zeichnet eine Linie zum dritten Punkt.
            path.lineTo(p1)  # Schließt den Pfad, um das Dreieck zu zeichnen.
            pen = QPen(QColor("yellow"), 1)  # Erstellt einen gelben Stift.
            current_triangle_line = QGraphicsPathItem(path)  # Erstellt ein QGraphicsPathItem mit dem Pfad.
            current_triangle_line.setPen(pen)  # Setzt den Stift für das Item.
            scene.addItem(current_triangle_line)  # Fügt die Linie zur Szene hinzu.
        else:  # Wenn kein Dreieck ausgewählt wurde.
            if current_triangle_line is not None:  # Wenn eine Linie vorhanden ist.
                scene.removeItem(current_triangle_line)  # Entfernt die Linie.
                current_triangle_line = None  # Setzt die Linienvariable zurück.
        
        # Offsets wie zuvor interpolieren
        interpolated_offsets = interpolate_position(ball_pos, interpolation_triangles, interpolation_offsets)  # Ruft die Interpolationsfunktion auf.
        
        if interpolated_offsets:  # Wenn Offsets erfolgreich interpoliert wurden.
            for i, player in enumerate(players):  # Iteriert über alle Spieler.
                if i < len(interpolated_offsets):  # Überprüft, ob ein Offset für den Spieler vorhanden ist.
                    offset = interpolated_offsets[i]  # Holt den interpolierten Offset.
                    new_position = QPointF(x + offset[0], y + offset[1])  # Berechnet die neue Spielerposition.
                    player.setPos(new_position)  # Setzt die neue Spielerposition.
                    player.updateShadow(x, y)  # Aktualisiert den Spielerschatten.
    
    def update_formation_markers(formations):  # Definiert eine Funktion zur Aktualisierung der Formationsmarker.
        # Aktualisiert visuelle Marker für jede gespeicherte defensive Formation
        # Alte Marker entfernen
        for marker in formation_markers:  # Iteriert über vorhandene Marker.
            if marker.scene():  # Überprüft, ob der Marker Teil einer Szene ist.
                scene.removeItem(marker)  # Entfernt den Marker aus der Szene.
        formation_markers.clear()  # Leert die Liste der Formationsmarker.
        
        # Neue Marker für jede Formation hinzufügen
        for i, form in enumerate(formations):  # Iteriert über die aktuellen Formationen.
            ball_pos = form["ball"]  # Holt die Ballposition der Formation.
            marker = FormationMarkerItem(ball_pos, i)  # Erstellt einen neuen Formationsmarker.
            scene.addItem(marker)  # Fügt den Marker zur Szene hinzu.
            formation_markers.append(marker)  # Fügt den Marker zur Liste hinzu.
        
        # Nach Marker-Aktualisierung Interpolationsdaten aktualisieren
        update_interpolation_data()  # Ruft die Funktion zur Aktualisierung der Interpolationsdaten auf.
    
    # Übergibt volleyball_field.scale als Skalierungsfaktor an das Panel
    def_panel = DefensivePositionsPanel(get_formation_callback=getFormation, scale_factor=volleyball_field.scale)  # Erstellt das DefensivePositionsPanel.
    def_panel.formationSelected.connect(apply_defensive_formation)  # Verbindet das formationSelected-Signal mit der apply_defensive_formation-Funktion.
    def_panel.formationsChanged.connect(update_formation_markers)  # Verbindet das formationsChanged-Signal mit der update_formation_markers-Funktion.
    main_layout.addWidget(def_panel)  # Fügt das Panel zum Hauptlayout hinzu.
    
    # Zonen-Callback für alle Spieler setzen
    for idx, player in enumerate(players):  # Iteriert über alle Spieler.
        player.player_index = idx  # Setzt den Index des Spielers.
        player.zone_update_callback = def_panel.update_zone  # Setzt den Callback für Zonenaktualisierungen.
    
    # TeamPanel rechts neben DefensivePositionsPanel
    # Callback zum Auslesen aktueller Spielernamen (unter dem Spieler)
    def get_player_names():  # Definiert eine Funktion zum Abrufen der aktuellen Spielernamen.
        return [player.name_label for player in players]  # Gibt eine Liste der Namenlabels der Spieler zurück.

    # Funktion zur Anwendung eines geladenen Teams
    def on_team_selected(names):  # Definiert eine Funktion, die aufgerufen wird, wenn ein Team ausgewählt wird.
        for i, player in enumerate(players):  # Iteriert über alle Spieler.
            if i < len(names):  # Überprüft, ob ein Name für den Spieler vorhanden ist.
                player.name_label = names[i]  # Setzt das Namenlabel des Spielers.
                player.name_text.setPlainText(names[i])  # Setzt den Text des Namenlabels.
                player.updateNameTextPosition()  # Aktualisiert die Position des Namenstextes.

    team_panel = TeamPanel(get_names_callback=get_player_names)  # Erstellt das TeamPanel.
    team_panel.teamSelected.connect(on_team_selected)  # Verbindet das teamSelected-Signal mit der on_team_selected-Funktion.
    main_layout.addWidget(team_panel)  # Fügt das TeamPanel zum Hauptlayout hinzu.
    # Erst nach Verbindung des Signals initiales Team laden
    team_panel.load_teams()  # Lädt die gespeicherten Teams.
    
    # Initialisierung der Marker mit aktuell geladenen Formationen
    update_formation_markers(def_panel.formations)  # Aktualisiert die Formationsmarker initial.
    
    # Verknüpft Ballpositionsänderungen mit Interpolationsfunktion
    ball.positionChanged.connect(interpolate_player_positions)  # Verbindet das positionChanged-Signal des Balls mit der Interpolationsfunktion.
    
    # Einrastfunktion: Überprüft Nähe des Balls zu gespeicherten Formationen und läd sie
    def snap_to_formation(x, y):  # Definiert eine Funktion zum Einrasten auf Formationen.
        snap_radius = 10  # Definiert den Radius, innerhalb dessen eingerastet wird (halbiert).
        # Suche nach nächster gespeicherter Formation
        for idx, form in enumerate(def_panel.formations):  # Iteriert über alle gespeicherten Formationen.
            fx, fy = form["ball"]  # Holt die Ballposition der Formation.
            if math.hypot(x - fx, y - fy) <= snap_radius:  # Überprüft, ob der Ball nahe genug an der Formation ist.
                saved = (fx, fy)  # Speichert die Ballposition der Formation.
                offs = [tuple(off) for off in form.get("offsets", [])]  # Holt die Offsets der Formation.
                zones = form.get("zones", [])  # Holt die Zonen der Formation.
                # Lade Formation und setze Listenauswahl
                apply_defensive_formation((saved, offs, zones))  # Wendet die Formation an.
                def_panel.positions_list.setCurrentRow(idx)  # Wählt die Formation in der Liste aus.
                def_panel.on_item_clicked(def_panel.positions_list.currentItem())  # Simuliert einen Klick auf das Listenelement.
                break  # Beendet die Schleife, da eine Formation gefunden und angewendet wurde.
    ball.positionChanged.connect(snap_to_formation)  # Verbindet das positionChanged-Signal des Balls mit der Einrastfunktion.
    
    main_widget.setWindowTitle("Volleyball Angriffssituation")  # Setzt den Fenstertitel.
    main_widget.resize(1600, 1600)  # Setzt die Größe des Hauptfensters.
    main_widget.show()  # Zeigt das Hauptfenster an.
    
    sys.exit(app.exec())  # Startet die Event-Loop der Anwendung und beendet das Programm beim Schließen.

if __name__ == '__main__':  # Überprüft, ob das Skript direkt ausgeführt wird.
    main()  # Ruft die Hauptfunktion auf.
