import math # Importiert das Modul math für mathematische Operationen
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsTextItem, QGraphicsRectItem, QMenu, QColorDialog # Importiert notwendige Klassen von PySide6.QtWidgets
from PySide6.QtGui import QBrush, QColor, QPen, QPainterPath, QRadialGradient # Importiert notwendige Klassen von PySide6.QtGui
from PySide6.QtCore import QRectF, Qt, QPointF # Importiert notwendige Klassen von PySide6.QtCore
from player_editor import PlayerEditorDialog  # Importiert den Dialog zur Spielerbearbeitung

# Use absolute imports instead of relative
from utils import DraggableEllipse, CourtDimensions # Importiert DraggableEllipse und CourtDimensions von utils

class ZoneItem(QGraphicsRectItem): # Definiert die Klasse ZoneItem, die von QGraphicsRectItem erbt
    """
    Repräsentiert eine Annahmezone mit Rechtsklick-Menü zum Löschen.
    """
    def __init__(self, rect, player_item, panel, color): # Konstruktor der Klasse
        super().__init__(rect) # Ruft den Konstruktor der Basisklasse auf
        # Erlaube Rechtsklick-Events und Hover
        self.setAcceptHoverEvents(True) # Aktiviert Hover-Events
        # Keine Maus-Buttons akzeptieren, damit Rechtsklicks an den Player weitergeleitet werden
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton) # Akzeptiert keine Mausklicks direkt
        self.player_item = player_item # Speichert das zugehörige Spieleritem
        self.panel = panel # Speichert das Panel, zu dem die Zone gehört
        self.color = color # Speichert die Farbe der Zone
        # Zeichne Zone über dem Feld (z=1)
        self.setZValue(100) # Setzt den Z-Wert für die Stapelreihenfolge
        # Kein Rahmen, nur Füllung
        self.setPen(QPen(Qt.PenStyle.NoPen)) # Kein Rand für die Zone
        c = QColor(color) # Erstellt ein QColor-Objekt
        # Halbe Transparenz erzwingen
        semi_alpha = max(1, color.alpha() // 2) # Berechnet die halbe Transparenz
        c.setAlpha(semi_alpha) # Setzt die Transparenz der Farbe
        self.setBrush(QBrush(c)) # Setzt die Füllung der Zone
#
    def mousePressEvent(self, event): # Methode zur Behandlung von Mausklicks
        # Klick auf den Spieler durchreichen, wenn Zone darüber liegt
        scene_pos = event.scenePos() # Holt die Position des Klicks in der Szene
        mapped = self.player_item.mapFromScene(scene_pos) # Mappt die Position auf das Spieleritem
        if self.player_item.shape().contains(mapped): # Prüft, ob der Klick innerhalb des Spieleritems war
            event.ignore() # Ignoriert das Event, damit das Spieleritem es behandeln kann
            return # Beendet die Methode
        # Rechtsklick: Kontextmenü für Bearbeiten/Löschen
        if event.button() == Qt.MouseButton.RightButton: # Prüft, ob es ein Rechtsklick war
            menu = QMenu() # Erstellt ein Kontextmenü
            edit_zone = menu.addAction("Zone bearbeiten") # Fügt eine Aktion zum Bearbeiten der Zone hinzu
            delete_zone = menu.addAction("Löschen") # Fügt eine Aktion zum Löschen der Zone hinzu
            edit_player = menu.addAction("Spieler bearbeiten") # Fügt eine Aktion zum Bearbeiten des Spielers hinzu
            action = menu.exec(event.screenPos()) # Zeigt das Menü an und holt die ausgewählte Aktion
            if action == delete_zone: # Wenn die Aktion "Löschen" war
                if self.panel and hasattr(self.panel, 'delete_zone_entry'): # Prüft, ob das Panel existiert und die Methode delete_zone_entry hat
                    r = self.rect() # Holt das Rechteck der Zone
                    c = self.color # Holt die Farbe der Zone
                    self.panel.delete_zone_entry( # Ruft die Methode zum Löschen des Zoneneintrags im Panel auf
                        self.player_item.player_index, # Übergibt den Spielerindex
                        [r.x(), r.y(), r.width(), r.height()], # Übergibt die Dimensionen der Zone
                        [c.red(), c.green(), c.blue(), c.alpha()] # Übergibt die Farbwerte der Zone
                    )
                if self.scene(): # Prüft, ob die Zone einer Szene hinzugefügt wurde
                    self.scene().removeItem(self) # Entfernt die Zone aus der Szene
            elif action == edit_zone: # Wenn die Aktion "Zone bearbeiten" war
                color = QColorDialog.getColor(self.color) # Öffnet einen Farbauswahldialog
                if color.isValid(): # Prüft, ob eine gültige Farbe ausgewählt wurde
                    self.color = color # Speichert die neue Farbe
                    c = QColor(color) # Erstellt ein QColor-Objekt mit der neuen Farbe
                    # Halbe Transparenz auch nach Farbänderung
                    semi_alpha = max(1, color.alpha() // 2) # Berechnet die halbe Transparenz
                    c.setAlpha(semi_alpha) # Setzt die Transparenz der Farbe
                    self.setBrush(QBrush(c)) # Setzt die Füllung der Zone mit der neuen Farbe
                    if self.panel and hasattr(self.panel, 'update_zone'): # Prüft, ob das Panel existiert und die Methode update_zone hat
                        r = self.rect() # Holt das Rechteck der Zone
                        self.panel.update_zone( # Ruft die Methode zum Aktualisieren der Zone im Panel auf
                            self.player_item.player_index, # Übergibt den Spielerindex
                            r, # Übergibt das Rechteck der Zone
                            color # Übergibt die neue Farbe
                        )
            elif action == edit_player: # Wenn die Aktion "Spieler bearbeiten" war
                # Spieler bearbeiten, wenn Zone das den Klick verdeckt
                editor = PlayerEditorDialog(self.player_item) # Erstellt einen Dialog zur Spielerbearbeitung
                editor.exec() # Führt den Dialog aus
            event.accept() # Akzeptiert das Event
            return # Beendet die Methode
        super().mousePressEvent(event) # Ruft die Methode der Basisklasse auf

    def contextMenuEvent(self, event): # Methode zur Behandlung von Kontextmenü-Events
        # Zonen ignorieren Kontext-Menü-Events, damit Spieler-Items es erhalten
        event.ignore() # Ignoriert das Event

class PlayerItem(DraggableEllipse): # Definiert die Klasse PlayerItem, die von DraggableEllipse erbt
    def __init__(self, rect, label="", ball=None, court_dims=None, name_label=None, player_index=None, zone_update_callback=None): # Konstruktor der Klasse
        super().__init__(rect, label) # Ruft den Konstruktor der Basisklasse auf
        # Setze einen sehr hohen Z-Wert für den Spieler selbst
        self.setZValue(1000)  # Setzt den Z-Wert für die Stapelreihenfolge sehr hoch
        # Ermögliche Rechtsklick für Kontextmenü und Links-Klick-Bewegung
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton) # Akzeptiert Links- und Rechtsklicks
        
        self.ball = ball  # Speichert das Ballobjekt
        self.court_dims = court_dims or CourtDimensions() # Setzt die Spielfeldmaße, Standardmaße wenn keine angegeben
        self.half_court = self.court_dims.height / 2 # Berechnet die Höhe des halben Spielfelds
        # setzt Bewegungsgrenze für den Spieler (Spielfeldgrenzen)
        boundary = QRectF(-30, self.half_court, self.court_dims.width + 60, self.half_court) # Definiert die Bewegungsgrenzen des Spielers
        self.set_movement_boundary(boundary) # Setzt die Bewegungsgrenzen

        # Erstellt den Blockschatten
        self.shadow = QGraphicsPathItem() # Erstellt ein QGraphicsPathItem für den Schatten
        self.shadow.setZValue(150)  # Stellt sicher, dass der Blockschatten über den Zonen liegt (z=100)
        # Setzt den Blockschatten-Pinsel auf Grau
        self.shadow.setBrush(QBrush(QColor(128, 128, 128, 128))) # Setzt die Füllfarbe des Schattens
        self.shadow.setPen(QPen(Qt.PenStyle.NoPen)) # Kein Rand für den Schatten
        
        self.label = label  # Speichert das Label des Spielers (z.B. Position)
        # Wenn kein eigener Name übergeben wurde, nehme das Positions-Label als Standard (MB)
        effective_name = name_label if name_label else label # Setzt den effektiven Namen (Name oder Label)
        self.name_label = effective_name # Speichert den effektiven Namen
        # Benutzerspezifisches Namens-Label unter dem Spieler
        self.name_text = QGraphicsTextItem(self.name_label, self) # Erstellt ein Textitem für den Namen
        font = self.name_text.font() # Holt die Schriftart des Textitems
        # Fett formatieren
        font.setBold(True) # Setzt die Schriftart auf fett
        orig_size = font.pointSize() if font.pointSize() > 0 else 12 # Holt die ursprüngliche Schriftgröße oder Standardgröße 12
        font.setPointSize(orig_size // 2) # Halbiert die Schriftgröße
        self.name_text.setFont(font) # Setzt die neue Schriftart
        self.name_text.setDefaultTextColor(QColor("black")) # Setzt die Textfarbe auf Schwarz
        # Positionierung durchführen
        self.updateNameTextPosition() # Aktualisiert die Position des Namenstextes
            
        # legt die Spieler-Index fest 
        self.player_index = player_index # Speichert den Index des Spielers
        self.zone_update_callback = zone_update_callback  # Speichert die Callback-Funktion für Zonenaktualisierungen
        # Mehrfach-Zonen pro Spieler
        self.zones_items = []  # Initialisiert eine Liste für Zonenitems
        # Annahmezone-Attribute initialisieren
        self.zone_definition_active = False # Flag, ob die Zonendefinition aktiv ist
        self.zone_start = None # Startpunkt der Zonendefinition
        self.zone_rect_item = None # Temporäres Rechteckitem während der Zonendefinition
        # Scene-View übernimmt die Zone-Zeichnung
            
    def updateShadow(self, ball_x, ball_y): # Methode zur Aktualisierung des Blockschattens
        player_center = self.scenePos() + self.rect().center() # Berechnet die Mittelpunktkoordinaten des Spielers
        # Zeigt den Blockschatten nur, wenn der Spieler innerhalb von 1 Meter zum Netz ist
        if abs(player_center.y() - self.court_dims.net_y) > self.court_dims.scale: # Prüft die Distanz zum Netz
            self.shadow.setPath(QPainterPath())  # Entfernt Blockschatten, wenn weiter als 1 Meter entfernt
            return # Beendet die Methode
        dx = player_center.x() - ball_x # Differenz der X-Koordinaten von Spieler und Ball
        dy = player_center.y() - ball_y # Differenz der Y-Koordinaten von Spieler und Ball
        d = math.hypot(dx, dy) # Berechnet die Distanz zwischen Spieler und Ball
        if d == 0: # Wenn die Distanz Null ist (Ball auf Spieler)
            return # Beendet die Methode
            
        # Spieler-Radius
        R = self.rect().width() / 2 # Berechnet den Radius des Spielers
        
        # Prüft ob der Blockschatten angezeigt werden soll
        if d + 2*R > 150: # Wenn die Distanz plus zweimal der Radius größer als 150 ist (heuristischer Wert)
            self.shadow.setPath(QPainterPath()) # Entfernt den Schatten
        else: # Andernfalls wird der Schatten berechnet und gezeichnet
            # Rest der Blockschatten-Berechnung
            theta = math.atan2(dy, dx) # Winkel zwischen Spieler und Ball
            alpha = math.asin(min(R/d, 1)) # Winkel des Tangentenabschnitts
            left_angle = theta - alpha # Linker Winkel des Schattenbereichs
            right_angle = theta + alpha # Rechter Winkel des Schattenbereichs
            arc_radius = 250 # Radius des Schattenbogens
            
            path = QPainterPath() # Erstellt einen neuen Pfad für den Schatten
            path.moveTo(ball_x, ball_y) # Bewegt den Startpunkt des Pfades zur Ballposition
            rect_arc = QRectF(ball_x - arc_radius, ball_y - arc_radius, # Definiert das Rechteck für den Schattenbogen
                             arc_radius * 2, arc_radius * 2)
            start_angle_deg = -math.degrees(left_angle) # Startwinkel des Bogens in Grad
            sweep_angle_deg = -math.degrees(right_angle - left_angle) # Ausdehnungswinkel des Bogens in Grad
            path.arcTo(rect_arc, start_angle_deg, sweep_angle_deg) # Fügt den Bogen zum Pfad hinzu
            path.lineTo(ball_x, ball_y) # Schließt den Pfad zur Ballposition
            self.shadow.setPath(path) # Setzt den berechneten Pfad für das Schattenitem
            
            # Erstellt Farbverlauf für Blockschatten mit grauen Farben
            gradient = QRadialGradient(QPointF(ball_x, ball_y), arc_radius) # Erstellt einen radialen Farbverlauf
            gradient.setColorAt(0.0, QColor(128, 128, 128, 0)) # Setzt die Farbe am Startpunkt des Verlaufs (transparent)
            fraction = d / arc_radius # Berechnet den Anteil der Distanz am Bogenradius
            fraction = max(0, min(fraction, 1)) # Stellt sicher, dass der Anteil zwischen 0 und 1 liegt
            gradient.setColorAt(fraction - 0.01, QColor(128, 128, 128, 0)) # Setzt eine transparente Farbe kurz vor der Distanz
            gradient.setColorAt(fraction, QColor(128, 128, 128, 128)) # Setzt eine halbtransparente graue Farbe an der Distanz
            gradient.setColorAt(0.9, QColor(128, 128, 128, 128)) # Setzt eine halbtransparente graue Farbe bei 90% des Radius
            gradient.setColorAt(1.0, QColor(128, 128, 128, 0)) # Setzt die Farbe am Endpunkt des Verlaufs (transparent)
            self.shadow.setBrush(QBrush(gradient)) # Setzt den Farbverlauf als Füllung für den Schatten
    
    def mouseMoveEvent(self, event): # Methode zur Behandlung von Mausbewegungen
        # rechteck aktualisieren während Zone-Definition 
        if getattr(self, 'zone_definition_active', False) and self.zone_rect_item: # Prüft, ob die Zonendefinition aktiv ist und ein temporäres Rechteck existiert
            current = event.scenePos() # Holt die aktuelle Mausposition in der Szene
            rect = QRectF(self.zone_start, current).normalized() # Erstellt ein normalisiertes Rechteck vom Startpunkt zur aktuellen Position
            self.zone_rect_item.setRect(rect) # Setzt das Rechteck des temporären Items
            return # Beendet die Methode
        # Standard-Bewegung
        super().mouseMoveEvent(event) # Ruft die Methode der Basisklasse für die Standardbewegung auf
        # Zentriere das untere Namens-Label nach Bewegung
        self.updateNameTextPosition() # Aktualisiert die Position des Namenstextes
        
        if self.ball: # Prüft, ob ein Ballobjekt vorhanden ist
            ball_rect = self.ball.boundingRect() # Holt das Begrenzungsrechteck des Balls
            # berechnet den Mittelpunkt des Balls
            ball_center = self.ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2) # Berechnet die Mittelpunktkoordinaten des Balls
            self.updateShadow(ball_center.x(), ball_center.y()) # Aktualisiert den Schatten basierend auf der Ballposition
    
    def mouseDoubleClickEvent(self, event): # Methode zur Behandlung von Doppelklicks
        # öffnet den Spieler-Editor
        editor = PlayerEditorDialog(self) # Erstellt einen Dialog zur Spielerbearbeitung
        editor.exec() # Führt den Dialog aus
        super().mouseDoubleClickEvent(event) # Ruft die Methode der Basisklasse auf

    def updateNameTextPosition(self): # Methode zur Aktualisierung der Position des Namenstextes
        """
        Zentriert das untere Namens-Label unter dem Spieler.
        """
        text_rect = self.name_text.boundingRect() # Holt das Begrenzungsrechteck des Textes
        rect = self.rect() # Holt das Begrenzungsrechteck des Spielers
        x = rect.x() + rect.width() / 2 - text_rect.width() / 2 # Berechnet die X-Position für zentrierten Text
        y = rect.y() + rect.height() + 2 # Berechnet die Y-Position unterhalb des Spielers
        self.name_text.setPos(x, y) # Setzt die Position des Namenstextes

    def mousePressEvent(self, event): # Methode zur Behandlung von Mausklicks
        # funktion ermöglicht die Zone-Definition
        scene_pos = event.scenePos() # Holt die Position des Klicks in der Szene
        mapped = self.mapFromScene(scene_pos) # Mappt die Position auf das Spieleritem
        # Wenn keine Zonendefinition aktiv, ignoriere werden klicks außerhalb des Spielers ignoriert
        if not getattr(self, 'zone_definition_active', False): # Prüft, ob die Zonendefinition nicht aktiv ist
            if not self.shape().contains(mapped): # Prüft, ob der Klick außerhalb der Form des Spielers war
                event.ignore() # Ignoriert das Event
                return # Beendet die Methode
        # Rechtsklick weiterleiten an contextMenuEvent
        if event.button() == Qt.MouseButton.RightButton: # Prüft, ob es ein Rechtsklick war
            event.ignore() # Ignoriert das Event, um es an contextMenuEvent weiterzuleiten
            return # Beendet die Methode
        # Linksklick: Starte Zone-Definition, wenn aktiv
        if getattr(self, 'zone_definition_active', False) and event.button() == Qt.MouseButton.LeftButton: # Prüft, ob Zonendefinition aktiv ist und es ein Linksklick war
            self.zone_start = event.scenePos() # Speichert den Startpunkt der Zone
            self.zone_rect_item = QGraphicsRectItem() # Erstellt ein temporäres Rechteckitem für die Zone
            self.zone_rect_item.setZValue(100) # Setzt den Z-Wert des temporären Rechtecks
            self.zone_rect_item.setPen(QPen(QColor("lightgray"), 1)) # Setzt einen hellgrauen Rand für das temporäre Rechteck
            self.zone_rect_item.setBrush(QBrush(QColor(0, 0, 0, 0))) # Setzt eine transparente Füllung für das temporäre Rechteck
            self.zone_rect_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton) # Das temporäre Rechteck akzeptiert keine Mausklicks
            self.zone_rect_item.setAcceptHoverEvents(False) # Das temporäre Rechteck akzeptiert keine Hover-Events
            self.scene().addItem(self.zone_rect_item) # Fügt das temporäre Rechteck zur Szene hinzu
            event.accept() # Akzeptiert das Event
            return # Beendet die Methode
        super().mousePressEvent(event) # Ruft die Methode der Basisklasse auf 

    def mouseReleaseEvent(self, event): # Methode zur Behandlung des Loslassens der Maustaste
        # wenn man maus links loslässt, wird die Zone-Definition beendet 
        if self.zone_definition_active and event.button() == Qt.MouseButton.LeftButton: # Prüft, ob Zonendefinition aktiv war und die linke Maustaste losgelassen wurde
            self.zone_definition_active = False # Deaktiviert die Zonendefinition
            self.ungrabMouse() # Gibt die Maus frei
            # Farbwahl (halbtransparent)
            color = QColorDialog.getColor(parent=None) # Öffnet einen Farbauswahldialog
            if color.isValid() and self.zone_rect_item: # Prüft, ob eine gültige Farbe ausgewählt wurde und das temporäre Rechteck existiert
                # ZoneItem anstelle des temporären Rechtecks erstellen
                rect = self.zone_rect_item.rect() # Holt das Rechteck des temporären Items
                panel = self.zone_update_callback.__self__ if hasattr(self.zone_update_callback, '__self__') else None # Holt das Panel von der Callback-Funktion
                zone_item = ZoneItem(rect, self, panel, color) # Erstellt ein neues ZoneItem
                self.scene().addItem(zone_item) # Fügt das ZoneItem zur Szene hinzu
                self.zones_items.append(zone_item) # Fügt das ZoneItem zur Liste der Zonen des Spielers hinzu
                # Panel speichern
                if panel and hasattr(panel, 'update_zone'): # Prüft, ob das Panel existiert und die Methode update_zone hat
                    panel.update_zone(self.player_index, rect, color) # Aktualisiert die Zone im Panel
                # Entfernen des temporäres Rechteck
                if self.zone_rect_item.scene(): # Prüft, ob das temporäre Rechteck einer Szene hinzugefügt wurde
                    self.zone_rect_item.scene().removeItem(self.zone_rect_item) # Entfernt das temporäre Rechteck aus der Szene
            elif self.zone_rect_item and self.zone_rect_item.scene(): # Wenn keine gültige Farbe ausgewählt wurde, aber ein temporäres Rechteck existiert
                # Abbruch: temporäres Rechteck entfernen
                self.scene().removeItem(self.zone_rect_item) # Entfernt das temporäre Rechteck aus der Szene
            # Referenz löschen
            self.zone_rect_item = None # Setzt die Referenz auf das temporäre Rechteck zurück
            return # Beendet die Methode
        super().mouseReleaseEvent(event) # Ruft die Methode der Basisklasse auf

    def addZone(self, rect: QRectF, color: QColor): # Methode zum Hinzufügen einer gespeicherten Zone
        """
        Fügt eine gespeicherte Annahmezone hinzu und zeigt sie an.
        """
        # Erzeuge interaktives ZoneItem wie in der Erstellung per Maus
        panel = self.zone_update_callback.__self__ if hasattr(self.zone_update_callback, '__self__') else None # Holt das Panel von der Callback-Funktion
        zone_item = ZoneItem(rect, self, panel, color) # Erstellt ein neues ZoneItem
        if self.scene(): # Prüft, ob der Spieler einer Szene hinzugefügt wurde
            # fügt die Zone zum Spielfeld hinzu
            self.scene().addItem(zone_item) # Fügt das ZoneItem zur Szene hinzu
        self.zones_items.append(zone_item) # Fügt das ZoneItem zur Liste der Zonen des Spielers hinzu

    def clearZones(self): # Methode zum Entfernen aller Zonen eines Spielers
        """
        Entfernt alle Annahmezonen vom Spieler.
        """
        for zi in self.zones_items: # Iteriert über alle Zonenitems des Spielers
            if zi.scene(): # Prüft, ob das Zonenitem einer Szene hinzugefügt wurde
                zi.scene().removeItem(zi) # Entfernt das Zonenitem aus der Szene
        self.zones_items.clear() # Leert die Liste der Zonenitems

    def contextMenuEvent(self, event): # Methode zur Behandlung von Kontextmenü-Events (erscheint beim Rechtsklick auf den Spieler)
        menu = QMenu() # Erstellt ein Kontextmenü
        add_zone = menu.addAction("Zone hinzufügen") # Fügt eine Aktion zum Hinzufügen einer Zone hinzu
        clear_zones = menu.addAction("Zonen löschen") # Fügt eine Aktion zum Löschen aller Zonen hinzu
        edit_player = menu.addAction("Name bearbeiten") # Fügt eine Aktion zum Bearbeiten des Spielernamens hinzu
        action = menu.exec(event.screenPos()) # Zeigt das Menü an und holt die ausgewählte Aktion
        if action == add_zone: # Wenn die Aktion "Zone hinzufügen" war
            # Starte Zone-Definition
            self.zone_definition_active = True # Aktiviert die Zonendefinition
            self.grabMouse() # Fängt Maus-Events ab, um die Zone zu zeichnen
        elif action == clear_zones: # Wenn die Aktion "Zonen löschen" war
            # Entferne alle Zonen inkl. Panel-Einträge
            for zi in list(self.zones_items): # Iteriert über eine Kopie der Liste der Zonenitems
                if self.zone_update_callback and hasattr(self.zone_update_callback.__self__, 'delete_zone_entry'): # Prüft, ob eine Callback-Funktion und die Panel-Methode existieren
                    r = zi.rect() # Holt das Rechteck der Zone
                    c = zi.color # Holt die Farbe der Zone
                    self.zone_update_callback.__self__.delete_zone_entry( # Ruft die Methode zum Löschen des Zoneneintrags im Panel auf
                        self.player_index, # Übergibt den Spielerindex
                        [r.x(), r.y(), r.width(), r.height()], # Übergibt die Dimensionen der Zone
                        [c.red(), c.green(), c.blue(), c.alpha()] # Übergibt die Farbwerte der Zone
                    )
                if zi.scene(): # Prüft, ob das Zonenitem einer Szene hinzugefügt wurde (entfernt die Zone aus der Szene)
                    zi.scene().removeItem(zi) # Entfernt das Zonenitem aus der Szene
            self.zones_items.clear() # Leert die Liste der Zonenitems
        elif action == edit_player: # Wenn die Aktion "Name bearbeiten" war
            editor = PlayerEditorDialog(self) # Erstellt einen Dialog zur Spielerbearbeitung
            editor.exec() # Führt den Dialog aus
        event.accept() # Akzeptiert das Event