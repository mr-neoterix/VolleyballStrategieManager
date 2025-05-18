from PyQt6.QtWidgets import QGraphicsItem  # Importiert QGraphicsItem als Basisklasse für eigene grafische Elemente.
from PyQt6.QtGui import QBrush, QPen, QColor  # Importiert Klassen für Pinsel, Stifte und Farben.
from PyQt6.QtCore import Qt, QRectF, QLineF  # Importiert Qt-Kernfunktionalitäten, QRectF für Rechtecke und QLineF für Linien.

class VolleyballField(QGraphicsItem):  # Definiert die Klasse für das Volleyballfeld, erbt von QGraphicsItem.
    def __init__(self, scale=30, parent=None):  # Konstruktor der Klasse, nimmt einen Maßstab und ein optionales Eltern-Element entgegen.
        super().__init__(parent)  # Ruft den Konstruktor der Basisklasse auf.
        self.scale = scale  # Speichert den Maßstab (Pixel pro Meter).
        self.court_width = 9 * scale  # Berechnet die Breite des Spielfelds in Pixeln (9 Meter).
        self.court_length = 18 * scale  # Berechnet die Länge des Spielfelds in Pixeln (18 Meter).
        self.net_y = self.court_length / 2  # Berechnet die y-Position der Netzlinie (Mitte des Feldes).
        self.overhang = 20  # Definiert einen Überhang in Pixeln für die Darstellung (z.B. für das Netz).
        # Setze Z-Wert so niedrig, dass das Feld immer im Hintergrund liegt.
        self.setZValue(-1000)  # Setzt den Z-Wert des Feldes, um sicherzustellen, dass es hinter anderen Elementen gezeichnet wird.

    def boundingRect(self):  # Definiert die Methode, die das äußere Rechteck des Elements zurückgibt.
        # Berücksichtige den Überhang
        return QRectF(-self.overhang, 0, self.court_width + 2*self.overhang, self.court_length)  # Gibt das Rechteck zurück, das das Feld inklusive Überhang umschließt.

    def paint(self, painter, option, widget):  # Definiert die Methode zum Zeichnen des Elements.
        # Färbe den Spielfeldboden in einer Holzfarbe (z. B. ein heller Holzton)
        wood_brush = QBrush(QColor(255, 169, 129, 100))  # Auftrag: SaddleBrown-ähnlich. Erstellt einen Pinsel mit einer holzähnlichen Farbe (mit Transparenz).
        field_pen = QPen(QColor("black"), 2)  # Erstellt einen schwarzen Stift mit einer Breite von 2 Pixeln für die Feldlinien.
        painter.setBrush(wood_brush)  # Setzt den Pinsel für den Maler.
        painter.setPen(field_pen)  # Setzt den Stift für den Maler.
        painter.drawRect(0, 0, self.court_width, self.court_length)  # Zeichnet das Rechteck des Spielfelds.

        # Zeichne das Netz (mit Überhang) als QLineF
        net_pen = QPen(QColor("grey"), 2)  # Erstellt einen grauen Stift für das Netz.
        painter.setPen(net_pen)  # Setzt den Netz-Stift für den Maler.
        net_line = QLineF(-self.overhang, self.net_y, self.court_width + self.overhang, self.net_y)  # Definiert die Linie für das Netz, die den Überhang berücksichtigt.
        painter.drawLine(net_line)  # Zeichnet die Netzlinie.

        # Zeichne 3-Meter-Linien als festen Bestandteil des Spielfelds
        line_pen = QPen(QColor("red"), 2, Qt.PenStyle.DashLine)  # Erstellt einen roten, gestrichelten Stift für die 3-Meter-Linien.
        painter.setPen(line_pen)  # Setzt den Linien-Stift für den Maler.
        # 3-Meter-Linie vor dem Netz
        y_attack = self.net_y - 3 * self.scale  # Berechnet die y-Position der Angriffslinie auf der oberen Feldhälfte.
        painter.drawLine(QLineF(0, y_attack, self.court_width, y_attack))  # Zeichnet die obere Angriffslinie.
        # 3-Meter-Linie hinter dem Netz
        y_defense = self.net_y + 3 * self.scale  # Berechnet die y-Position der Angriffslinie auf der unteren Feldhälfte.
        painter.drawLine(QLineF(0, y_defense, self.court_width, y_defense))  # Zeichnet die untere Angriffslinie.

# Globale Spielerliste für VolleyballField hinzufügen
players = []  # Initialisiert eine globale Liste zur Speicherung der Spielerobjekte.