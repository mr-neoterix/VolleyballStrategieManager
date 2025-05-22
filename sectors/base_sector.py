from PySide6.QtWidgets import QGraphicsPathItem # Importiert QGraphicsPathItem von PyQt6.QtWidgets
from PySide6.QtGui import QPen, QPainterPath # Importiert QPen und QPainterPath von PyQt6.QtGui
from PySide6.QtCore import Qt, QPointF # Importiert Qt und QPointF von PyQt6.QtCore

class BaseSector(QGraphicsPathItem): # Basisklasse für Sektoren (Blockschatten, Schlagwinkel)
    def __init__(self, center:QPointF=QPointF(), z_index=0): # Konstruktor der Klasse
        super().__init__() # Ruft den Konstruktor der Basisklasse auf
        self.center = center # Speichert den Mittelpunkt des Sektors
        self.path = QPainterPath() # Initialisiert ein leeres QPainterPath-Objekt
        self.setZValue(z_index) # Setzt den Z-Wert für die Stapelreihenfolge
        self.setPen(QPen(Qt.PenStyle.NoPen)) # Setzt den Stift auf keinen Rand
        
    def set_center(self, x, y): # Methode zum Setzen des Mittelpunkts des Sektors
        self.center = QPointF(x, y) # Setzt den Mittelpunkt des Sektors
        
    def update_path(self): # Methode zur Aktualisierung des Pfades (soll in Unterklassen überschrieben werden)
        """In Unterklassen überschreiben, um den Pfad zu aktualisieren"""
        pass # Platzhalter, Implementierung erfolgt in abgeleiteten Klassen
        
    def set_brush(self, brush): # Methode zum Setzen des Füllpinsels
        """Legt den Pinsel für diesen Sektor fest"""
        self.setBrush(brush) # Setzt den Füllpinsel für das Item
