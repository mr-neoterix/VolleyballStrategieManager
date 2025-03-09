from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox, QLabel, QWidget
from PyQt5.QtCore import Qt

class PlayerEditorDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle("Spieler bearbeiten")
        
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Editable player name
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(player.label if hasattr(player, "label") else "")
        form_layout.addRow("Name:", self.name_edit)
        
        # Create editors for each sector: primary, wide, backward
        self.editors = {}
        for key in ["primary", "wide", "backward"]:
            sector = player.sectors.get(key)
            if sector:
                group_label = QLabel(f"{key.capitalize()} Sector", self)
                form_layout.addRow(group_label)
                
                # Angle width editor
                angle_spin = QDoubleSpinBox(self)
                angle_spin.setRange(0, 360)
                angle_spin.setValue(sector.params.angle_width)
                form_layout.addRow("Winkel (°):", angle_spin)
                
                # Max radius editor (convert to meters)
                radius_spin = QDoubleSpinBox(self)
                radius_spin.setRange(0, 20)
                # get current meters: radius in pixels divided by scale
                current_radius = sector.params.max_radius_meters if hasattr(sector.params, "max_radius_meters") else 0
                radius_spin.setValue(current_radius)
                form_layout.addRow("Länge (m):", radius_spin)
                
                self.editors[key] = {"angle": angle_spin, "radius": radius_spin}
                
        main_layout.addLayout(form_layout)
        
        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        main_layout.addWidget(self.buttonBox)
        
    def accept(self):
        # Update player name if exists
        new_name = self.name_edit.text()
        if hasattr(self.player, "label"):
            self.player.label = new_name
        # Update each sector parameters
        for key, edits in self.editors.items():
            sector = self.player.sectors.get(key)
            if sector:
                sector.params.angle_width = edits["angle"].value()
                sector.params.max_radius_meters = edits["radius"].value()
                # Refresh the sector with current positions
                player_center = self.player.scenePos() + self.player.rect().center()
                ball = self.player.ball
                if ball:
                    ball_rect = ball.rect()
                    ball_center = ball.scenePos() + ball_rect.center()
                    sector.updatePosition(player_center.x(), player_center.y(), ball_center.x(), ball_center.y())
        super().accept()
