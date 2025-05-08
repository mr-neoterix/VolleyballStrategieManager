from PyQt6.QtCore import QPointF, QRectF, pyqtSignal, QObject
from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtGui import QBrush, QPen, QColor, QPainter
from PyQt6.QtCore import Qt

# Verwendung absoluten Imports
from utils import CourtDimensions
from volleyball_field import players

class BallItem(QGraphicsObject):
    """Repräsentiert den Ball auf dem Volleyballfeld als interaktives Grafikobjekt"""
    positionChanged = pyqtSignal(float, float)
    
    def __init__(self, rect, label="", court_dimensions=None, parent=None):
        """
        Initialisiert den Ball mit einer bestimmten Größe und Position
        
        Parameter:
            rect: Rechteck, das Größe und Position definiert
            label: Optionaler Text für den Ball (meist nicht verwendet)
            court_dimensions: Spielfeldmaße oder None für Standardmaße
            parent: Übergeordnetes Qt-Element
        """
        super().__init__(parent)
        self._rect = rect
        self.setFlags(self.flags() | 
                      QGraphicsObject.GraphicsItemFlag.ItemIsSelectable | 
                      QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.court_dims = court_dimensions or CourtDimensions()
        self.half_court = self.court_dims.height / 2
        self.attack_sector = None
        # Setzt den Bewegungsbereich für den Ball (Spielfeldgrenzen)
        self.movement_boundary = QRectF(0, 0, self.court_dims.width, self.half_court)
        # Aussehen des Balls
        self._brush = QBrush(QColor("yellow"))
        self._pen = QPen(QColor("black"), 2)
    
    def boundingRect(self):
        """
        Gibt die Begrenzung des Balls zurück, wird von Qt für Zeichnen und Kollisionserkennung benötigt
        """
        return self._rect
    
    def paint(self, painter: QPainter, option, widget=None):
        """
        Zeichnet den Ball mit drei farbigen Segmenten (blau, gelb, orange)
        
        Diese Methode wird automatisch aufgerufen, wenn der Ball gerendert werden muss
        """
        # Zeichnet nur die farbigen Segmente ohne äußere Ränder
        # Volles Rechteck für die Segmente verwenden
        # Blaues Segment (lückenlos, 120°)
        painter.setBrush(QBrush(QColor("#1E90FF")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(self._rect, 30 * 16, 120 * 16)
        # Gelbes Segment (lückenlos, 120°)
        painter.setBrush(QBrush(QColor("#FFD700")))
        painter.drawPie(self._rect, 150 * 16, 120 * 16)
        # Oranges Segment (lückenlos, 120°)
        painter.setBrush(QBrush(QColor("#FFCC66")))
        painter.drawPie(self._rect, 270 * 16, 120 * 16)
    
    def link_sector(self, sector):
        """
        Verbindet den Ball mit einem Angriffssektor, der die möglichen Angriffswege anzeigt
        
        Parameter:
            sector: Das AttackSector-Objekt, das mit dem Ball verknüpft werden soll
        """
        self.attack_sector = sector
        self.update_sector_position()
    
    def update_sector_position(self):
        """
        Aktualisiert die Position des Angriffssektors basierend auf der aktuellen Ballposition
        """
        if self.attack_sector:
            center = self.scenePos() + QPointF(self._rect.width()/2, self._rect.height()/2)
            self.attack_sector.updatePosition(center.x(), center.y())
    
    def set_movement_boundary(self, boundary: QRectF):
        """
        Definiert die Grenzen, innerhalb derer der Ball bewegt werden kann
        
        Parameter:
            boundary: Rechteck, das die Bewegungsgrenzen definiert
        """
        self.movement_boundary = boundary
    
    def setBrush(self, brush):
        """
        Setzt den Füllpinsel für den Ball
        
        Parameter:
            brush: QBrush-Objekt für die Füllung
        """
        self._brush = brush
        self.update()
        
    def setPen(self, pen):
        self._pen = pen
        self.update()
    
    def mouseMoveEvent(self, event):
        """
        Behandelt Mausbewegungen beim Ziehen des Balls
        
        Beschränkt die Bewegung auf das Spielfeld und aktualisiert alle abhängigen Objekte
        (Angriffssektor, Spieler-Schatten) wenn der Ball bewegt wird.
        """
        old_pos = self.pos()
        super().mouseMoveEvent(event)
        # Wendet Bewegungsbeschränkungen an
        if self.movement_boundary:
            pos = self.pos()
            r = self.boundingRect()
            min_x = self.movement_boundary.x()
            max_x = self.movement_boundary.x() + self.movement_boundary.width() - r.width()
            new_x = max(min_x, min(pos.x(), max_x))
            min_y = self.movement_boundary.y()
            max_y = self.movement_boundary.y() + self.movement_boundary.height() - r.height()
            new_y = max(min_y, min(pos.y(), max_y))
            if new_x != pos.x() or new_y != pos.y():
                self.setPos(new_x, new_y)
        if old_pos != self.pos():   # wenn alte und neue Position unterschiedlich sind, wird die Position des Balls aktualisiert
            ball_center = self.scenePos() + QPointF(self._rect.width()/2, self._rect.height()/2)
            self.update_sector_position()
            for player in players:
                player.updateShadow(ball_center.x(), ball_center.y())
            self.positionChanged.emit(ball_center.x(), ball_center.y())
