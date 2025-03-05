from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget, 
                             QInputDialog, QMessageBox, QGraphicsPathItem, QHBoxLayout,
                             QFileDialog, QGraphicsTextItem)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QPainterPath, QBrush
from defense_positions import DefensePositionManager, DefensePosition
import math

class DefensePositionLines(QGraphicsPathItem):
    def __init__(self, position_manager):
        super().__init__()
        self.position_manager = position_manager
        self.setZValue(1)  # Unter den Spielern aber über dem Spielfeld
        self.setPen(QPen(QColor(255, 0, 0, 128), 1))  # Halbtransparentes Rot
        self.setBrush(QBrush(Qt.NoBrush))
        self.circle_radius = 5  # Radius der roten Kreise
        self.update_path()
    
    def orientation(self, p, q, r):
        """Berechnet die Orientierung des Punktes r relativ zur Linie pq."""
        val = (q.y() - p.y()) * (r.x() - q.x()) - (q.x() - p.x()) * (r.y() - q.y())
        if val == 0:
            return 0  # Kollinear
        return 1 if val > 0 else 2  # Im Uhrzeigersinn oder gegen den Uhrzeigersinn
    
    def in_circle(self, a, b, c, d):
        """Prüft, ob Punkt d im Umkreis des Dreiecks abc liegt."""
        # Berechne die Determinante
        ax, ay = a.x(), a.y()
        bx, by = b.x(), b.y()
        cx, cy = c.x(), c.y()
        dx, dy = d.x(), d.y()
        
        det = (ax - dx) * ((by - dy) * (cx*2 + cy*2 - dx*2 - dy*2) - (cy - dy) * (bx*2 + by*2 - dx*2 - dy*2)) - \
              (ay - dy) * ((bx - dx) * (cx*2 + cy*2 - dx*2 - dy*2) - (cx - dx) * (bx*2 + by*2 - dx*2 - dy*2)) + \
              (ax*2 + ay*2 - dx*2 - dy*2) * ((bx - dx) * (cy - dy) - (cx - dx) * (by - dy))
        
        return det > 0
    
    def find_containing_triangle(self, point, points):
        """Findet das Dreieck, das den Punkt enthält."""
        if len(points) < 3:
            return None
            
        # Erstelle eine Liste aller möglichen Dreiecke
        triangles = []
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                for k in range(j + 1, len(points)):
                    p1, p2, p3 = points[i], points[j], points[k]
                    
                    # Prüfe, ob der Punkt im Dreieck liegt
                    if self.point_in_triangle(point, p1, p2, p3):
                        # Prüfe, ob ein anderer Punkt im Dreieck liegt
                        has_point_inside = False
                        for p in points:
                            if p not in [p1, p2, p3] and self.point_in_triangle(p, p1, p2, p3):
                                has_point_inside = True
                                break
                        
                        if not has_point_inside:
                            triangles.append((p1, p2, p3))
        
        # Wenn kein Dreieck gefunden wurde, nehme das Dreieck mit dem kleinsten Umkreis
        if not triangles:
            return self.find_nearest_triangle(point, points)
        
        return triangles[0]
    
    def point_in_triangle(self, p, p1, p2, p3):
        """Prüft, ob ein Punkt in einem Dreieck liegt."""
        def sign(p1, p2, p3):
            return (p1.x() - p3.x()) * (p2.y() - p3.y()) - (p2.x() - p3.x()) * (p1.y() - p3.y())
        
        d1 = sign(p, p1, p2)
        d2 = sign(p, p2, p3)
        d3 = sign(p, p3, p1)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def find_nearest_triangle(self, point, points):
        """Findet das Dreieck mit dem kleinsten Umkreis."""
        if len(points) < 3:
            return None
            
        min_circumradius = float('inf')
        best_triangle = None
        
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                for k in range(j + 1, len(points)):
                    p1, p2, p3 = points[i], points[j], points[k]
                    circumradius = self.calculate_circumradius(p1, p2, p3)
                    
                    if circumradius < min_circumradius:
                        min_circumradius = circumradius
                        best_triangle = (p1, p2, p3)
        
        return best_triangle
    
    def calculate_circumradius(self, p1, p2, p3):
        """Berechnet den Umkreisradius eines Dreiecks."""
        # Berechne die Seitenlängen
        a = math.sqrt((p2.x() - p3.x())**2 + (p2.y() - p3.y())**2)
        b = math.sqrt((p3.x() - p1.x())**2 + (p3.y() - p1.y())**2)
        c = math.sqrt((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)
        
        # Berechne den Umkreisradius mit der Formel R = abc/(4A)
        # wobei A die Fläche des Dreiecks ist
        s = (a + b + c) / 2
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        if area == 0:
            return float('inf')
        return (a * b * c) / (4 * area)
    
    def update_path(self):
        path = QPainterPath()
        positions = self.position_manager.get_all_positions()
        
        if not positions:
            self.setPath(path)
            return
            
        # Extrahiere die Ballpositionen
        ball_positions = [pos.ball_pos for pos in positions]
        
        # Finde den aktuellen Ball
        current_ball = None
        for item in self.scene().items():
            if hasattr(item, 'is_ball') and item.is_ball:
                current_ball = item
                break
        
        if current_ball:
            # Berechne die Position des aktuellen Balls
            current_pos = current_ball.scenePos() + current_ball.rect().center()
            
            # Finde das umgebende Dreieck
            triangle = self.find_containing_triangle(current_pos, ball_positions)
            
            # Zeichne die Linien des Dreiecks
            if triangle:
                p1, p2, p3 = triangle
                path.moveTo(p1.x(), p1.y())
                path.lineTo(p2.x(), p2.y())
                path.lineTo(p3.x(), p3.y())
                path.lineTo(p1.x(), p1.y())
        
        # Zeichne die roten Kreise für alle Positionen
        for pos in ball_positions:
            circle = QPainterPath()
            circle.addEllipse(pos, self.circle_radius, self.circle_radius)
            path.addPath(circle)
        
        self.setPath(path)

class DefensePositionList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.position_manager = DefensePositionManager()
        self.position_lines = None
        self.setFixedWidth(200)  # Fixe Breite für das gesamte Widget
        self.setup_ui()
        # Lade die gespeicherten Positionen
        self.position_manager.load_positions()
        self.update_list()
        
        # Erstelle Text-Item für die Koordinatenanzeige
        self.coord_label = QGraphicsTextItem()
        self.coord_label.setDefaultTextColor(Qt.white)
        self.coord_label.setZValue(1000)  # Über allen anderen Elementen
        if self.parent() and self.parent().scene():
            self.parent().scene().addItem(self.coord_label)
    
    def pixel_to_meters(self, x: float, y: float) -> tuple[float, float]:
        """Konvertiert Pixel-Koordinaten in Meter."""
        # Hole den scale-Faktor aus dem VolleyballField
        scale = 30  # 30 Pixel pro Meter (definiert in VolleyballField)
        meters_x = x / scale
        meters_y = y / scale
        return meters_x, meters_y
    
    def update_coord_label(self, x: float, y: float):
        """Aktualisiert die Koordinatenanzeige."""
        meters_x, meters_y = self.pixel_to_meters(x, y)
        self.coord_label.setPlainText(f"Ball: {meters_x:.1f}m / {meters_y:.1f}m")
        # Positioniere das Label oben links
        self.coord_label.setPos(10, 10)
        # Aktualisiere die Linien
        if self.position_lines:
            self.position_lines.update_path()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Keine Ränder
        
        # Speichern-Button
        self.save_button = QPushButton("Aktuelle Stellung speichern")
        self.save_button.clicked.connect(self.save_current_position)
        layout.addWidget(self.save_button)
        
        # Liste der Stellungen
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.load_position)
        layout.addWidget(self.list_widget)
        
        # Button-Layout für Löschen
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Keine Ränder
        self.delete_button = QPushButton("Stellung löschen")
        self.delete_button.clicked.connect(self.delete_position)
        self.delete_button.setEnabled(False)  # Initial deaktiviert
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Erstelle die Linien
        self.position_lines = DefensePositionLines(self.position_manager)
        if self.parent() and self.parent().scene():
            self.parent().scene().addItem(self.position_lines)
        
        # Verbinde die Auswahl in der Liste mit dem Lösch-Button
        self.list_widget.itemSelectionChanged.connect(self.update_delete_button)
    
    def update_delete_button(self):
        """Aktiviert/Deaktiviert den Lösch-Button basierend auf der Auswahl."""
        self.delete_button.setEnabled(bool(self.list_widget.selectedItems()))
    
    def delete_position(self):
        """Löscht die ausgewählte Stellung."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
            
        index = self.list_widget.row(selected_items[0])
        position = self.position_manager.get_position(index)
        
        # Bestätigungsdialog
        reply = QMessageBox.question(
            self, 
            "Stellung löschen",
            f"Möchten Sie die Stellung '{position.name}' wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Entferne die Position aus dem Manager
            self.position_manager.delete_position(index)
            self.update_list()
            # Aktualisiere die Linien
            if self.position_lines:
                self.position_lines.update_path()
    
    def save_current_position(self):
        # Hole die aktuelle Szene
        scene = self.parent().scene()
        if not scene:
            return
        
        # Hole den Ball
        ball = None
        for item in scene.items():
            if hasattr(item, 'is_ball') and item.is_ball:
                ball = item
                break
        
        if not ball:
            QMessageBox.warning(self, "Fehler", "Kein Ball gefunden!")
            return
        
        # Hole die Spielerpositionen
        player_positions = {}
        for item in scene.items():
            if isinstance(item, self.parent().player_class):
                player_positions[item.label] = item.scenePos() + item.rect().center()
        
        if not player_positions:
            QMessageBox.warning(self, "Fehler", "Keine Spieler gefunden!")
            return
        
        # Berechne den vorgeschlagenen Namen mit Koordinaten in Metern
        ball_center = ball.scenePos() + ball.rect().center()
        meters_x, meters_y = self.pixel_to_meters(ball_center.x(), ball_center.y())
        suggested_name = f"Ball ({meters_x:.1f}m/{meters_y:.1f}m)"
        
        # Frage nach dem Namen der Stellung
        name, ok = QInputDialog.getText(self, "Stellung speichern", 
                                      "Bitte geben Sie einen Namen für diese Stellung ein:",
                                      text=suggested_name)
        if ok and name:
            # Speichere die Stellung
            self.position_manager.add_position(
                name,
                ball_center,
                player_positions
            )
            self.update_list()
            # Aktualisiere die Linien
            if self.position_lines:
                self.position_lines.update_path()
    
    def load_position(self, item):
        index = self.list_widget.row(item)
        position = self.position_manager.get_position(index)
        
        # Hole die aktuelle Szene
        scene = self.parent().scene()
        if not scene:
            return
        
        # Setze die Ballposition
        ball = None
        for scene_item in scene.items():
            if hasattr(scene_item, 'is_ball') and scene_item.is_ball:
                ball = scene_item
                ball_rect = ball.rect()
                ball.setPos(position.ball_pos.x() - ball_rect.width()/2,
                           position.ball_pos.y() - ball_rect.height()/2)
                # Aktualisiere die Koordinatenanzeige
                self.update_coord_label(position.ball_pos.x(), position.ball_pos.y())
                # Aktualisiere den Angriffssektor des Balls
                ball.update_sector_position()
                break
        
        if not ball:
            return
            
        # Aktualisiere die Ballposition für die Sektoren
        ball_center = ball.scenePos() + ball.rect().center()
        
        # Setze die Spielerpositionen und aktualisiere ihre Sektoren
        for scene_item in scene.items():
            if isinstance(scene_item, self.parent().player_class):
                if scene_item.label in position.player_positions:
                    player_pos = position.player_positions[scene_item.label]
                    player_rect = scene_item.rect()
                    scene_item.setPos(player_pos.x() - player_rect.width()/2,
                                    player_pos.y() - player_rect.height()/2)
                    # Aktualisiere die Sektoren und Schatten
                    scene_item.updateShadow(ball_center.x(), ball_center.y())
                    scene_item.update_sectors(ball_center.x(), ball_center.y())
    
    def update_list(self):
        self.list_widget.clear()
        for position in self.position_manager.get_all_positions():
            self.list_widget.addItem(position.name)
    
    def check_and_interpolate(self, ball_pos):
        # Prüfe, ob wir genug Positionen haben
        if len(self.position_manager.get_all_positions()) < 2:
            return
            
        # Interpoliere die Spielerpositionen
        interpolated_positions = self.position_manager.interpolate_positions(ball_pos)
        
        # Aktualisiere die Spielerpositionen
        scene = self.parent().scene()
        if not scene:
            return
        
        for scene_item in scene.items():
            if isinstance(scene_item, self.parent().player_class):
                if scene_item.label in interpolated_positions:
                    player_pos = interpolated_positions[scene_item.label]
                    player_rect = scene_item.rect()
                    scene_item.setPos(player_pos.x() - player_rect.width()/2,
                                    player_pos.y() - player_rect.height()/2) 