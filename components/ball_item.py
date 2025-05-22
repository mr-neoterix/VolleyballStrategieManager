from PySide6.QtCore import QPointF, QRectF, Signal, QObject # Importiert notwendige Klassen von PyQt6.QtCore
from PySide6.QtWidgets import QGraphicsObject # Importiert QGraphicsObject von PyQt6.QtWidgets
from PySide6.QtGui import QBrush, QPen, QColor, QPainter # Importiert notwendige Klassen von PyQt6.QtGui
from PySide6.QtCore import Qt # Importiert Qt von PyQt6.QtCore

# Verwendung absoluten Imports
from utils import CourtDimensions # Importiert CourtDimensions von utils
from volleyball_field import players # Importiert die Spielerliste vom Volleyballfeld

class BallItem(QGraphicsObject): # Definiert die Klasse BallItem, die von QGraphicsObject erbt
    """Repräsentiert den Ball auf dem Volleyballfeld als interaktives Grafikobjekt"""
    positionChanged = Signal(float, float) # Signal, das bei Positionsänderung des Balls ausgesendet wird
    
    def __init__(self, rect, label="", court_dimensions=None, parent=None): # Konstruktor der Klasse
        """
        Initialisiert den Ball mit einer bestimmten Größe und Position
        
        Parameter:
            rect: Rechteck, das Größe und Position definiert
            label: Optionaler Text für den Ball (meist nicht verwendet)
            court_dimensions: Spielfeldmaße oder None für Standardmaße
            parent: Übergeordnetes Qt-Element
        """
        super().__init__(parent) # Ruft den Konstruktor der Basisklasse auf
        self._rect = rect # Speichert das Rechteck des Balls
        self.setFlags(self.flags() | # Setzt Flags für das Grafikobjekt
                      QGraphicsObject.GraphicsItemFlag.ItemIsSelectable | # Der Ball ist auswählbar
                      QGraphicsObject.GraphicsItemFlag.ItemIsMovable) # Der Ball ist beweglich
        self.court_dims = court_dimensions or CourtDimensions() # Setzt die Spielfeldmaße, Standardmaße wenn keine angegeben
        self.half_court = self.court_dims.height / 2 # Berechnet die Höhe des halben Spielfelds
        self.attack_sector = None # Initialisiert den Angriffssektor als None
        # Setzt den Bewegungsbereich für den Ball (Spielfeldgrenzen)
        self.movement_boundary = QRectF(0, 0, self.court_dims.width, self.half_court) # Definiert die Bewegungsgrenzen des Balls
        # Aussehen des Balls
        self._brush = QBrush(QColor("yellow")) # Setzt die Füllfarbe des Balls auf Gelb
        self._pen = QPen(QColor("black"), 2) # Setzt den Stift für den Rand des Balls auf Schwarz mit einer Dicke von 2
    
    def boundingRect(self): # Methode zur Rückgabe des Begrenzungsrechtecks
        """
        Gibt die Begrenzung des Balls zurück, wird von Qt für Zeichnen und Kollisionserkennung benötigt
        """
        return self._rect # Gibt das Rechteck des Balls zurück
    
    def paint(self, painter: QPainter, option, widget=None): # Methode zum Zeichnen des Balls
        """
        Zeichnet den Ball mit drei farbigen Segmenten (blau, gelb, orange)
        
        Diese Methode wird automatisch aufgerufen, wenn der Ball gerendert werden muss
        """
        # Zeichnet nur die farbigen Segmente ohne äußere Ränder
        # Volles Rechteck für die Segmente verwenden
        # Blaues Segment (lückenlos, 120°)
        painter.setBrush(QBrush(QColor("#1E90FF"))) # Setzt die Füllfarbe für das blaue Segment
        painter.setPen(Qt.PenStyle.NoPen) # Kein Rand für die Segmente
        painter.drawPie(self._rect, 30 * 16, 120 * 16) # Zeichnet das blaue Kreissegment
        # Gelbes Segment (lückenlos, 120°)
        painter.setBrush(QBrush(QColor("#FFD700"))) # Setzt die Füllfarbe für das gelbe Segment
        painter.drawPie(self._rect, 150 * 16, 120 * 16) # Zeichnet das gelbe Kreissegment
        # Oranges Segment (lückenlos, 120°)
        painter.setBrush(QBrush(QColor("#FFCC66"))) # Setzt die Füllfarbe für das orange Segment
        painter.drawPie(self._rect, 270 * 16, 120 * 16) # Zeichnet das orange Kreissegment
    
    def link_sector(self, sector): # Methode zur Verknüpfung mit einem Angriffssektor
        """
        Verbindet den Ball mit einem Angriffssektor, der die möglichen Angriffswege anzeigt
        
        Parameter:
            sector: Das AttackSector-Objekt, das mit dem Ball verknüpft werden soll
        """
        self.attack_sector = sector # Speichert den Angriffssektor
        self.update_sector_position() # Aktualisiert die Position des Sektors
    
    def update_sector_position(self): # Methode zur Aktualisierung der Sektorposition
        """
        Aktualisiert die Position des Angriffssektors basierend auf der aktuellen Ballposition
        """
        if self.attack_sector: # Prüft, ob ein Angriffssektor vorhanden ist
            center = self.scenePos() + QPointF(self._rect.width()/2, self._rect.height()/2) # Berechnet die Mittelpunktkoordinaten des Balls in der Szene
            self.attack_sector.updatePosition(center.x(), center.y()) # Aktualisiert die Position des Angriffssektors
    
    def set_movement_boundary(self, boundary: QRectF): # Methode zum Setzen der Bewegungsgrenzen
        """
        Definiert die Grenzen, innerhalb derer der Ball bewegt werden kann
        
        Parameter:
            boundary: Rechteck, das die Bewegungsgrenzen definiert
        """
        self.movement_boundary = boundary # Speichert die neuen Bewegungsgrenzen
    
    def setBrush(self, brush): # Methode zum Setzen des Füllpinsels
        """
        Setzt den Füllpinsel für den Ball
        
        Parameter:
            brush: QBrush-Objekt für die Füllung
        """
        self._brush = brush # Speichert den neuen Füllpinsel
        self.update() # Löst eine Neuzeichnung des Objekts aus
        
    def setPen(self, pen): # Methode zum Setzen des Stiftes
        self._pen = pen # Speichert den neuen Stift
        self.update() # Löst eine Neuzeichnung des Objekts aus
    
    def mouseMoveEvent(self, event): # Methode zur Behandlung von Mausbewegungen
        """
        Behandelt Mausbewegungen beim Ziehen des Balls
        
        Beschränkt die Bewegung auf das Spielfeld und aktualisiert alle abhängigen Objekte
        (Angriffssektor, Spieler-Schatten) wenn der Ball bewegt wird.
        """
        old_pos = self.pos() # Speichert die alte Position des Balls
        super().mouseMoveEvent(event) # Ruft die Methode der Basisklasse auf, um die Standard-Mausbewegung zu handhaben
        # Wendet Bewegungsbeschränkungen an
        if self.movement_boundary: # Prüft, ob Bewegungsgrenzen definiert sind
            pos = self.pos() # Holt die aktuelle Position
            r = self.boundingRect() # Holt das Begrenzungsrechteck
            min_x = self.movement_boundary.x() # Minimale X-Koordinate
            max_x = self.movement_boundary.x() + self.movement_boundary.width() - r.width() # Maximale X-Koordinate
            new_x = max(min_x, min(pos.x(), max_x)) # Stellt sicher, dass die X-Position innerhalb der Grenzen liegt
            min_y = self.movement_boundary.y() # Minimale Y-Koordinate
            max_y = self.movement_boundary.y() + self.movement_boundary.height() - r.height() # Maximale Y-Koordinate
            new_y = max(min_y, min(pos.y(), max_y)) # Stellt sicher, dass die Y-Position innerhalb der Grenzen liegt
            if new_x != pos.x() or new_y != pos.y(): # Wenn sich die Position geändert hat, um innerhalb der Grenzen zu bleiben
                self.setPos(new_x, new_y) # Setzt die neue Position
        if old_pos != self.pos():   # wenn alte und neue Position unterschiedlich sind, wird die Position des Balls aktualisiert
            ball_center = self.scenePos() + QPointF(self._rect.width()/2, self._rect.height()/2) # Berechnet die Mittelpunktkoordinaten des Balls in der Szene
            self.update_sector_position() # Aktualisiert die Position des Angriffssektors
            for player in players: # Iteriert über alle Spieler
                player.updateShadow(ball_center.x(), ball_center.y()) # Aktualisiert den Schatten jedes Spielers basierend auf der Ballposition
            self.positionChanged.emit(ball_center.x(), ball_center.y()) # Sendet das Signal für die Positionsänderung mit den neuen Koordinaten 