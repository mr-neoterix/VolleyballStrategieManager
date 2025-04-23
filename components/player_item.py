import math
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsTextItem, QGraphicsRectItem, QMenu, QColorDialog
from PyQt6.QtGui import QBrush, QColor, QPen, QPainterPath, QRadialGradient
from PyQt6.QtCore import QRectF, Qt, QPointF
from player_editor import PlayerEditorDialog  # added import

# Use absolute imports instead of relative
from utils import DraggableEllipse, CourtDimensions

class PlayerItem(DraggableEllipse):
    def __init__(self, rect, label="", ball=None, court_dims=None, name_label=None, player_index=None, zone_update_callback=None):
        super().__init__(rect, label)
        # Set a very high z-value for the player itself
        self.setZValue(1000)  # Ensure player is always on top
        # Ermögliche Rechtsklick für Kontextmenü und Links-Klick-Bewegung
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton)
        
        self.ball = ball  # Referenz zum Ball
        self.court_dims = court_dims or CourtDimensions()
        self.half_court = self.court_dims.height / 2
        # New: Set movement boundary for the ball (court boundaries)
        boundary = QRectF(-30, self.half_court, self.court_dims.width + 60, self.half_court)
        self.set_movement_boundary(boundary)

        # Erstelle den Schlagschatten
        self.shadow = QGraphicsPathItem()
        self.shadow.setZValue(10)  # Higher than default but below player
        # Set the shadow brush to gray instead of green
        self.shadow.setBrush(QBrush(QColor(128, 128, 128, 128)))
        self.shadow.setPen(QPen(Qt.PenStyle.NoPen))
        
        self.label = label  # store position label
        # Wenn kein eigener Name übergeben wurde, nehme das Positions-Label als Standard
        effective_name = name_label if name_label else label
        self.name_label = effective_name
        # Zusatz: Benutzerspezifisches Namens-Label unter dem Spieler
        self.name_text = QGraphicsTextItem(self.name_label, self)
        # Schriftgröße halbieren
        font = self.name_text.font()
        # Fett formatieren
        font.setBold(True)
        orig_size = font.pointSize() if font.pointSize() > 0 else 12
        font.setPointSize(orig_size // 2)
        self.name_text.setFont(font)
        self.name_text.setDefaultTextColor(QColor("black"))
        # Positionierung initial durchführen
        self.updateNameTextPosition()
            
        # Callback für das Speichern der Zone in Panel
        self.player_index = player_index
        self.zone_save_callback = zone_update_callback  # Funktion(player_index, QRectF, QColor)
        # Mehrfach-Zonen pro Spieler
        self.zones_items = []  # gespeicherte QGraphicsRectItem Objekte
        # Annahmezone-Attribute initialisieren
        self.zone_definition_active = False
        self.zone_start = None
        self.zone_rect_item = None
        # Hinweis: Scene-View übernimmt die Zone-Zeichnung
            
    def updateShadow(self, ball_x, ball_y):
        player_center = self.scenePos() + self.rect().center()
        # Only show block shadow if player is within 1 meter of the net
        if abs(player_center.y() - self.court_dims.net_y) > self.court_dims.scale:
            self.shadow.setPath(QPainterPath())  # remove shadow if farther than 1 meter
            return
        dx = player_center.x() - ball_x
        dy = player_center.y() - ball_y
        d = math.hypot(dx, dy)
        if d == 0:
            return
            
        # Spieler-Radius
        R = self.rect().width() / 2
        
        # Check if shadow should be shown
        if d + 2*R > 150:
            self.shadow.setPath(QPainterPath())
        else:
            # Rest of shadow calculation
            theta = math.atan2(dy, dx)
            alpha = math.asin(min(R/d, 1))
            left_angle = theta - alpha
            right_angle = theta + alpha
            arc_radius = 250
            
            path = QPainterPath()
            path.moveTo(ball_x, ball_y)
            rect_arc = QRectF(ball_x - arc_radius, ball_y - arc_radius,
                             arc_radius * 2, arc_radius * 2)
            start_angle_deg = -math.degrees(left_angle)
            sweep_angle_deg = -math.degrees(right_angle - left_angle)
            path.arcTo(rect_arc, start_angle_deg, sweep_angle_deg)
            path.lineTo(ball_x, ball_y)
            self.shadow.setPath(path)
            
            # Create gradient for shadow using gray colors
            gradient = QRadialGradient(QPointF(ball_x, ball_y), arc_radius)
            gradient.setColorAt(0.0, QColor(128, 128, 128, 0))
            fraction = d / arc_radius
            fraction = max(0, min(fraction, 1))
            gradient.setColorAt(fraction - 0.01, QColor(128, 128, 128, 0))
            gradient.setColorAt(fraction, QColor(128, 128, 128, 128))
            gradient.setColorAt(0.9, QColor(128, 128, 128, 128))
            gradient.setColorAt(1.0, QColor(128, 128, 128, 0))
            self.shadow.setBrush(QBrush(gradient))
    
    def mouseMoveEvent(self, event):
        # Während Zone-Definition: aktualisiere Rechteck
        if getattr(self, 'zone_definition_active', False) and self.zone_rect_item:
            current = event.scenePos()
            rect = QRectF(self.zone_start, current).normalized()
            self.zone_rect_item.setRect(rect)
            return
        # Standard-Bewegungslogik
        super().mouseMoveEvent(event)
        # Zentriere das untere Namens-Label nach Bewegung
        self.updateNameTextPosition()
        
        if self.ball:
            ball_rect = self.ball.boundingRect()
            ball_center = self.ball.scenePos() + QPointF(ball_rect.width()/2, ball_rect.height()/2)
            self.updateShadow(ball_center.x(), ball_center.y())
    
    def mouseDoubleClickEvent(self, event):
        editor = PlayerEditorDialog(self)
        editor.exec()
        super().mouseDoubleClickEvent(event)

    def updateNameTextPosition(self):
        """
        Zentriert das untere Namens-Label unter dem Spieler.
        """
        text_rect = self.name_text.boundingRect()
        rect = self.rect()
        x = rect.x() + rect.width() / 2 - text_rect.width() / 2
        y = rect.y() + rect.height() + 2
        self.name_text.setPos(x, y)

    def mousePressEvent(self, event):
        # Rechtsklick: Zeige Annahmezone-Option
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            define_action = menu.addAction("Annahmezone definieren")
            # Ermittle globale Bildschirmkoordinaten
            pos = event.screenPos()
            # Falls pos ein QPointF ist, konvertiere zu QPoint
            if hasattr(pos, 'toPoint'):
                pos = pos.toPoint()
            selected = menu.exec(pos)
            if selected == define_action:
                # Aktiviere Zone-Definition und fange alle Mausklicks ab
                self.zone_definition_active = True
                self.grabMouse()
            return
        # Linksklick: Starte Zone-Definition, wenn aktiv
        if self.zone_definition_active and event.button() == Qt.MouseButton.LeftButton:
            self.zone_start = event.scenePos()
            # Erstelle temporäres Rechteck
            self.zone_rect_item = QGraphicsRectItem()
            # Zeichne Zone über dem Feld, aber unter allen anderen Elementen (z=1)
            self.zone_rect_item.setZValue(1)
            self.zone_rect_item.setPen(QPen(QColor("lightgray"), 1))
            self.zone_rect_item.setBrush(QBrush(QColor(0, 0, 0, 0)))
            # Temporäres Rechteck Events deaktivieren
            self.zone_rect_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            self.zone_rect_item.setAcceptHoverEvents(False)
            self.scene().addItem(self.zone_rect_item)
            event.accept()
            return
        # Andernfalls Standard-Verhalten (Bewegung etc.)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # Abschluss der Zone-Definition
        if self.zone_definition_active and event.button() == Qt.MouseButton.LeftButton:
            # Beende Zone-Definition
            self.zone_definition_active = False
            self.ungrabMouse()
            # Farbwahl (halbtransparent enforced in main/App)
            color = QColorDialog.getColor(parent=None)
            if color.isValid() and self.zone_rect_item:
                # Setze Farbe auf das temporäre Rechteck
                self.zone_rect_item.setBrush(QBrush(color))
                # Füge Zone zu gespeicherter Liste hinzu
                self.zones_items.append(self.zone_rect_item)
                # Callback speichern
                if callable(self.zone_save_callback) and self.player_index is not None:
                    self.zone_save_callback(self.player_index, self.zone_rect_item.rect(), color)
            else:
                # Abbruch: Rechteck entfernen
                self.scene().removeItem(self.zone_rect_item)
            # Entferne temporäre Referenz, behalte QGraphicsRectItem in zones_items
            self.zone_rect_item = None
            return
        super().mouseReleaseEvent(event)

    def addZone(self, rect: QRectF, color: QColor):
        """
        Fügt eine gespeicherte Annahmezone hinzu und zeigt sie an.
        """
        zone_item = QGraphicsRectItem(rect)
        # Zone über dem Feld, unter Spielern/anderen Elementen
        zone_item.setZValue(1)
        # Rand und halbtransparente Füllung
        zone_item.setPen(QPen(QColor("lightgray"), 1))
        color.setAlpha(color.alpha() if color.alpha() else 200)
        zone_item.setBrush(QBrush(color))
        # Füge zur Szene hinzu
        if self.scene():
            self.scene().addItem(zone_item)
        # Merke
        self.zones_items.append(zone_item)

    def clearZones(self):
        """
        Entfernt alle Annahmezonen vom Spieler.
        """
        for zi in self.zones_items:
            if zi.scene():
                zi.scene().removeItem(zi)
        self.zones_items.clear()
