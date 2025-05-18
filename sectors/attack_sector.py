import math # Importiert das Modul math für mathematische Operationen
from PyQt6.QtCore import Qt, QPointF # Importiert Qt und QPointF von PyQt6.QtCore
from PyQt6.QtGui import QBrush, QColor, QPainterPath, QRadialGradient, QPixmap, QPainter, QTransform # Importiert notwendige Klassen von PyQt6.QtGui
from .base_sector import BaseSector # Importiert die Basisklasse BaseSector

class AttackSector(BaseSector): # Definiert die Klasse AttackSector, die von BaseSector erbt
    def __init__(self, ball_pos:QPointF, court_width=270, court_height=540, net_y=270, radius=300): # Konstruktor der Klasse
        super().__init__(ball_pos, z_index=2) # Ruft den Konstruktor der Basisklasse auf und initialisiert den Sektor mit der angegebenen Ballposition und einem Z-Index von 2
        self.ball_pos = ball_pos # Speichert die Ballposition
        self.court_width = court_width # Speichert die Breite des Spielfelds
        self.court_height = court_height # Speichert die Höhe des Spielfelds
        self.net_y = net_y # Speichert die Y-Koordinate des Netzes
        self.radius = radius # Speichert den Radius des Sektors (wird hier nicht direkt für den Pfad verwendet, aber für den Gradienten)
        self.update_path() # Aktualisiert den Pfad des Sektors
        
    def updatePosition(self, ball_x, ball_y): # Methode zur Aktualisierung der Sektorposition basierend auf der Ballposition
        # Aktualisiert die Ballposition mit den angegebenen Koordinaten
        self.ball_pos = QPointF(ball_x, ball_y) # Setzt die neue Ballposition
        self.update_path() # Aktualisiert den Pfad des Sektors
        
    def update_path(self): # Methode zur Aktualisierung des Pfades und des Aussehens des Sektors
        path = QPainterPath() # Erstellt ein neues QPainterPath-Objekt
        
        # Definiert die Positionen der Netzenden
        left_net = QPointF(0, self.net_y) # Linkes Netzende
        right_net = QPointF(self.court_width, self.net_y) # Rechtes Netzende
        
        # Dynamischer Radius: Berechnet den verfügbaren Platz vom Ball zum unteren Spielfeldrand
        dynamic_radius = self.net_y * 2 - self.ball_pos.y() # Berechnet den dynamischen Radius basierend auf der Ballposition und der Netzhöhe
        
        # Berechnet die Winkel vom Ball zu den beiden Netzenden
        # Diese Winkel bestimmen die Grenzen des Angriffssektors
        angle_left = math.degrees(math.atan2(self.ball_pos.y() - left_net.y(), # Berechnet den Winkel zum linken Netzende
                                            left_net.x() - self.ball_pos.x()))
        angle_right = math.degrees(math.atan2(self.ball_pos.y() - right_net.y(), # Berechnet den Winkel zum rechten Netzende
                                            right_net.x() - self.ball_pos.x()))
        
        # Zeichnet den Bogen des Angriffssektors
        start_angle = angle_left # Startwinkel des Bogens
        sweep_angle = angle_right - angle_left # Ausdehnungswinkel des Bogens
        
        path.moveTo(self.ball_pos.x(), self.ball_pos.y()) # Bewegt den Startpunkt des Pfades zur Ballposition
        path.arcTo(self.ball_pos.x() - dynamic_radius, self.ball_pos.y() - dynamic_radius, # Definiert das Rechteck für den Bogen
                dynamic_radius * 2, dynamic_radius * 2, # Breite und Höhe des Rechtecks
                start_angle, sweep_angle) # Start- und Ausdehnungswinkel
        path.lineTo(self.ball_pos.x(), self.ball_pos.y()) # Schließt den Pfad zur Ballposition
        self.setPath(path) # Setzt den erstellten Pfad für das Sektoritem
        
        # Erstellt den Farbverlauf für den Angriffssektor
        self._create_attack_gradient(dynamic_radius) # Ruft die Methode zur Erstellung des Farbverlaufs auf
        
    def _create_attack_gradient(self, radius): # Private Methode zur Erstellung des Farbverlaufs
        # Erstellt eine Zeichenfläche für den Farbverlauf
        size = int(radius * 2) # Größe der Pixmap basierend auf dem Radius
        if size <= 0: # Wenn die Größe ungültig ist
            return # Beendet die Methode
            
        combined = QPixmap(size, size) # Erstellt eine Pixmap für den kombinierten Farbverlauf
        combined.fill(QColor(0, 0, 0, 0))  # Füllt die Pixmap mit transparenter Farbe (Transparenter Hintergrund)
        
        painter = QPainter(combined) # Erstellt einen QPainter zum Zeichnen auf der Pixmap
        # Erzeugt einen radialen Farbverlauf vom Ball nach außen
        radial = QRadialGradient(QPointF(size/2, size/2), radius) # Erstellt einen radialen Farbverlauf
        radial.setColorAt(0.0, QColor(255, 0, 0, 255))   # Setzt die Farbe am Startpunkt (Rot nahe am Ball (hohe Angriffsintensität))
        radial.setColorAt(1.0, QColor(255, 255, 0, 255)) # Setzt die Farbe am Endpunkt (Gelb am Rand (niedrigere Intensität))
        painter.setBrush(QBrush(radial)) # Setzt den Farbverlauf als Füllpinsel für den Painter
        painter.setPen(Qt.PenStyle.NoPen) # Kein Rand für die Zeichnung
        painter.drawRect(0, 0, size, size) # Zeichnet ein Rechteck mit dem Farbverlauf
        painter.end() # Beendet den Painter
        
        # Fügt Transparenz hinzu (50%)
        temp = QPixmap(size, size) # Erstellt eine temporäre Pixmap
        temp.fill(QColor(0, 0, 0, 0)) # Füllt die temporäre Pixmap mit transparenter Farbe
        painter2 = QPainter(temp) # Erstellt einen zweiten Painter für die temporäre Pixmap
        painter2.setOpacity(0.5) # Setzt die Deckkraft auf 50%
        painter2.drawPixmap(0, 0, combined) # Zeichnet die ursprüngliche Pixmap mit Deckkraft auf die temporäre Pixmap
        painter2.end() # Beendet den zweiten Painter
        combined = temp # Weist die temporäre Pixmap (mit Transparenz) der combined-Variable zu
        
        # Positioniert den Farbverlauf auf dem Spielfeld passend zur Ballposition
        combined_brush = QBrush(combined) # Erstellt einen Füllpinsel aus der kombinierten Pixmap
        transform = QTransform() # Erstellt eine Transformation
        transform.translate(self.ball_pos.x() - size/2, self.ball_pos.y() - size/2) # Verschiebt die Transformation zur korrekten Position
        combined_brush.setTransform(transform) # Wendet die Transformation auf den Füllpinsel an
        
        self.setBrush(combined_brush) # Setzt den erstellten Füllpinsel für das Sektoritem
