import math  # Importiert das math-Modul für mathematische Operationen.
from PySide6.QtCore import QPointF  # Importiert QPointF von PySide6 für die Arbeit mit 2D-Punkten mit Fließkommazahlen.
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem  # Importiert Klassen für grafische Elemente wie Ellipsen und Text.
from PySide6.QtGui import QBrush, QPen, QColor  # Importiert Klassen für Pinsel, Stifte und Farben.
from PySide6.QtCore import Qt, QRectF  # Importiert Qt-Kernfunktionalitäten und QRectF für Rechtecke mit Fließkommazahlen.

# Konstanten
DEFAULT_SCALE = 30  # Definiert den Standardmaßstab: 30 Pixel pro Meter.

class CourtDimensions:  # Definiert eine Klasse zur Speicherung und Berechnung von Spielfeldabmessungen.
    def __init__(self, scale=DEFAULT_SCALE):  # Konstruktor der Klasse, nimmt einen optionalen Maßstab entgegen.
        self.scale = scale  # Speichert den Maßstab.
        self.width = 9 * scale  # Berechnet die Breite des Spielfelds.
        self.height = 18 * scale  # Berechnet die Höhe des Spielfelds.
        self.net_y = 9 * scale  # Definiert die y-Position der Netzlinie.
        self.attack_line_y = self.net_y - 3 * scale  # Berechnet die y-Position der Angriffslinie (auf der eigenen Seite, daher Subtraktion).
        self.defense_line_y = self.net_y + 3 * scale  # Berechnet die y-Position der (gegnerischen) Angriffslinie (aus Sicht der eigenen Seite).

def calculate_distance(p1: QPointF, p2: QPointF) -> float:  # Definiert eine Funktion zur Abstandsberechnung zwischen zwei QPointF-Punkten.
    """Berechnet den Abstand zwischen zwei Punkten"""  # Docstring der Funktion.
    dx = p2.x() - p1.x()  # Berechnet die Differenz der x-Koordinaten.
    dy = p2.y() - p1.y()  # Berechnet die Differenz der y-Koordinaten.
    return math.sqrt(dx*dx + dy*dy)  # Gibt den euklidischen Abstand zurück.

def calculate_angle(from_point: QPointF, to_point: QPointF) -> float:  # Definiert eine Funktion zur Winkelberechnung zwischen zwei QPointF-Punkten.
    """Berechnet den Winkel in Grad von einem Punkt zu einem anderen"""  # Docstring der Funktion.
    dx = to_point.x() - from_point.x()  # Berechnet die Differenz der x-Koordinaten.
    dy = to_point.y() - from_point.y()  # Berechnet die Differenz der y-Koordinaten.
    return (-math.degrees(math.atan2(dy, dx))) % 360  # Gibt den Winkel in Grad zurück (im Uhrzeigersinn, 0° ist rechts).

def get_intersection_with_net(player_pos: QPointF, ball_pos: QPointF, net_y: float) -> QPointF:  # Definiert eine Funktion zur Berechnung des Schnittpunkts einer Linie mit dem Netz.
    """Berechnet den Schnittpunkt der Linie zwischen Spieler und Ball mit dem Netz"""  # Docstring der Funktion.
    dx = ball_pos.x() - player_pos.x()  # Differenz der x-Koordinaten zwischen Ball und Spieler.
    dy = ball_pos.y() - player_pos.y()  # Differenz der y-Koordinaten zwischen Ball und Spieler.
    
    # Prüft, ob beide Punkte auf der gleichen Seite des Netzes sind
    if (player_pos.y() < net_y and ball_pos.y() < net_y) or \
       (player_pos.y() > net_y and ball_pos.y() > net_y):  # Bedingung: Beide Punkte unterhalb des Netzes.
        return None  # Gibt None zurück, wenn kein Schnittpunkt mit dem Netz möglich ist.
    
    # Behandelt den Fall einer horizontalen Linie
    if dy == 0:  # Wenn die y-Differenz null ist (horizontale Linie).
        return QPointF(player_pos.x(), net_y)  # Gibt einen Punkt auf der Netzlinie mit der x-Koordinate des Spielers zurück (oder des Balls, da y identisch).
    
    # Berechnet den Schnittpunkt mit der Geradengleichung
    intersection_x = player_pos.x() + (net_y - player_pos.y()) * dx / dy  # Berechnet die x-Koordinate des Schnittpunkts.
    return QPointF(intersection_x, net_y)  # Gibt den Schnittpunkt als QPointF zurück.

class DraggableEllipse(QGraphicsEllipseItem):  # Definiert eine Klasse für eine ziehbare Ellipse, die von QGraphicsEllipseItem erbt.
    def __init__(self, rect, label=""):  # Konstruktor der Klasse, nimmt ein Rechteck (QRectF) und ein optionales Label entgegen.
        super().__init__(rect)  # Ruft den Konstruktor der Basisklasse auf.
        # Setzt Flags für bewegbare Grafikelemente in PySide6
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)  # Macht das Element auswähl- und bewegbar.
        self.setBrush(QBrush(QColor("blue")))  # Setzt die Füllfarbe der Ellipse auf Blau.
        # Verwendet QColor("black") statt Qt.black
        self.setPen(QPen(QColor("black"), 2))  # Setzt den Rand der Ellipse auf Schwarz mit einer Breite von 2 Pixeln.
        if label:  # Wenn ein Label angegeben wurde.
            text = QGraphicsTextItem(label, self)  # Erstellt ein QGraphicsTextItem als Kind dieser Ellipse.
            font = text.font()  # Holt die aktuelle Schriftart des Textes.
            original_size = font.pointSize() if font.pointSize() > 0 else 12  # Bestimmt die ursprüngliche Schriftgröße oder verwendet 12 als Standard.
            font.setPointSize(original_size // 2)  # Halbiert die Schriftgröße.
            text.setFont(font)  # Setzt die neue Schriftart.
            text.setDefaultTextColor(QColor("white"))  # Setzt die Textfarbe auf Weiß.
            text.setPos(rect.x() + rect.width()/2 - text.boundingRect().width()/2,  # Zentriert den Text horizontal in der Ellipse.
                        rect.y() + rect.height()/2 - text.boundingRect().height()/2)  # Zentriert den Text vertikal in der Ellipse.
        self.movement_boundary: QRectF = None  # Initialisiert die Bewegungsgrenze als None.

    def set_movement_boundary(self, boundary: QRectF):  # Definiert eine Methode zum Setzen der Bewegungsgrenze.
        self.movement_boundary = boundary  # Speichert das übergebene Rechteck als Bewegungsgrenze.

    def mouseMoveEvent(self, event):  # Überschreibt das mouseMoveEvent, um die Bewegung zu beschränken.
        super().mouseMoveEvent(event)  # Ruft das mouseMoveEvent der Basisklasse auf, um die Standardbewegung auszuführen.
        if self.movement_boundary:  # Wenn eine Bewegungsgrenze gesetzt ist.
            pos = self.pos()  # Holt die aktuelle Position des Elements.
            r = self.rect()  # Holt das Rechteck des Elements (Größe).
            min_x = self.movement_boundary.x()  # Minimale x-Koordinate der Grenze.
            max_x = self.movement_boundary.x() + self.movement_boundary.width() - r.width()  # Maximale x-Koordinate der Grenze unter Berücksichtigung der Elementbreite.
            new_x = max(min_x, min(pos.x(), max_x))  # Beschränkt die x-Position auf die Grenzwerte.
            min_y = self.movement_boundary.y()  # Minimale y-Koordinate der Grenze.
            max_y = self.movement_boundary.y() + self.movement_boundary.height() - r.height()  # Maximale y-Koordinate der Grenze unter Berücksichtigung der Elementhöhe.
            new_y = max(min_y, min(pos.y(), max_y))  # Beschränkt die y-Position auf die Grenzwerte.
            if new_x != pos.x() or new_y != pos.y():  # Wenn die Position angepasst werden musste.
                self.setPos(new_x, new_y)  # Setzt die neue, beschränkte Position.
