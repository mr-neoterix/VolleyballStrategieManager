from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QLineEdit, QPushButton, QGroupBox)
from PyQt5.QtCore import Qt

class PlayerEditDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle("Spieler bearbeiten")
        self.setModal(True)
        
        # Layout erstellen
        layout = QVBoxLayout()
        
        # Label-Bearbeitung
        label_group = QGroupBox("Spieler-Label")
        label_layout = QHBoxLayout()
        self.label_edit = QLineEdit(player.label)
        label_layout.addWidget(QLabel("Label:"))
        label_layout.addWidget(self.label_edit)
        label_group.setLayout(label_layout)
        layout.addWidget(label_group)
        
        # Sektoren-Bearbeitung
        sectors_group = QGroupBox("Sektoren")
        sectors_layout = QVBoxLayout()
        
        # Primary Sektor
        primary_layout = QVBoxLayout()
        # Winkel
        primary_angle_layout = QHBoxLayout()
        primary_angle_layout.addWidget(QLabel("Primary Winkel:"))
        self.primary_slider = QSlider(Qt.Horizontal)
        self.primary_slider.setRange(1, 240)
        self.primary_slider.setValue(int(player.sectors["primary"].params.angle_width))
        self.primary_value_label = QLabel(f"{self.primary_slider.value()}°")
        primary_angle_layout.addWidget(self.primary_slider)
        primary_angle_layout.addWidget(self.primary_value_label)
        primary_layout.addLayout(primary_angle_layout)
        # Radius
        primary_radius_layout = QHBoxLayout()
        primary_radius_layout.addWidget(QLabel("Primary Radius:"))
        self.primary_radius_slider = QSlider(Qt.Horizontal)
        self.primary_radius_slider.setRange(10, 100)  # 1.0m bis 10.0m in 0.1m Schritten
        self.primary_radius_slider.setValue(int(player.sectors["primary"].params.max_radius_meters * 10))
        self.primary_radius_label = QLabel(f"{self.primary_radius_slider.value()/10:.1f}m")
        primary_radius_layout.addWidget(self.primary_radius_slider)
        primary_radius_layout.addWidget(self.primary_radius_label)
        primary_layout.addLayout(primary_radius_layout)
        sectors_layout.addLayout(primary_layout)
        
        # Wide Sektor
        wide_layout = QVBoxLayout()
        # Winkel
        wide_angle_layout = QHBoxLayout()
        wide_angle_layout.addWidget(QLabel("Wide Winkel:"))
        self.wide_slider = QSlider(Qt.Horizontal)
        self.wide_slider.setRange(1, 240)
        self.wide_slider.setValue(int(player.sectors["wide"].params.angle_width))
        self.wide_value_label = QLabel(f"{self.wide_slider.value()}°")
        wide_angle_layout.addWidget(self.wide_slider)
        wide_angle_layout.addWidget(self.wide_value_label)
        wide_layout.addLayout(wide_angle_layout)
        # Radius
        wide_radius_layout = QHBoxLayout()
        wide_radius_layout.addWidget(QLabel("Wide Radius:"))
        self.wide_radius_slider = QSlider(Qt.Horizontal)
        self.wide_radius_slider.setRange(10, 100)  # 1.0m bis 10.0m in 0.1m Schritten
        self.wide_radius_slider.setValue(int(player.sectors["wide"].params.max_radius_meters * 10))
        self.wide_radius_label = QLabel(f"{self.wide_radius_slider.value()/10:.1f}m")
        wide_radius_layout.addWidget(self.wide_radius_slider)
        wide_radius_layout.addWidget(self.wide_radius_label)
        wide_layout.addLayout(wide_radius_layout)
        sectors_layout.addLayout(wide_layout)
        
        # Backward Sektor (automatisch)
        backward_layout = QVBoxLayout()
        # Winkel
        backward_angle_layout = QHBoxLayout()
        backward_angle_layout.addWidget(QLabel("Backward Winkel:"))
        self.backward_value_label = QLabel(f"{360 - self.wide_slider.value()}°")
        backward_angle_layout.addWidget(self.backward_value_label)
        backward_layout.addLayout(backward_angle_layout)
        # Radius
        backward_radius_layout = QHBoxLayout()
        backward_radius_layout.addWidget(QLabel("Backward Radius:"))
        self.backward_radius_slider = QSlider(Qt.Horizontal)
        self.backward_radius_slider.setRange(10, 100)  # 1.0m bis 10.0m in 0.1m Schritten
        self.backward_radius_slider.setValue(int(player.sectors["backward"].params.max_radius_meters * 10))
        self.backward_radius_label = QLabel(f"{self.backward_radius_slider.value()/10:.1f}m")
        backward_radius_layout.addWidget(self.backward_radius_slider)
        backward_radius_layout.addWidget(self.backward_radius_label)
        backward_layout.addLayout(backward_radius_layout)
        sectors_layout.addLayout(backward_layout)
        
        sectors_group.setLayout(sectors_layout)
        layout.addWidget(sectors_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Speichern")
        cancel_button = QPushButton("Abbrechen")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Verbindungen
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        # Slider-Verbindungen
        self.primary_slider.valueChanged.connect(self.update_primary_sector)
        self.wide_slider.valueChanged.connect(self.update_wide_sector)
        self.primary_radius_slider.valueChanged.connect(self.update_primary_radius)
        self.wide_radius_slider.valueChanged.connect(self.update_wide_radius)
        self.backward_radius_slider.valueChanged.connect(self.update_backward_radius)
    
    def update_primary_sector(self, value):
        self.player.sectors["primary"].params.angle_width = value
        self.player.sectors["primary"].update_path()
        self.primary_value_label.setText(f"{value}°")
    
    def update_wide_sector(self, value):
        self.player.sectors["wide"].params.angle_width = value
        self.player.sectors["wide"].update_path()
        self.wide_value_label.setText(f"{value}°")
        # Aktualisiere den Backward-Winkel
        backward_angle = 360 - value
        self.player.sectors["backward"].params.angle_width = backward_angle
        self.player.sectors["backward"].update_path()
        self.backward_value_label.setText(f"{backward_angle}°")
    
    def update_primary_radius(self, value):
        radius_meters = value / 10.0  # Konvertiere von 0.1m-Schritten zu Metern
        self.player.sectors["primary"].params.max_radius_meters = radius_meters
        self.player.sectors["primary"].update_path()
        self.primary_radius_label.setText(f"{radius_meters:.1f}m")
    
    def update_wide_radius(self, value):
        radius_meters = value / 10.0  # Konvertiere von 0.1m-Schritten zu Metern
        self.player.sectors["wide"].params.max_radius_meters = radius_meters
        self.player.sectors["wide"].update_path()
        self.wide_radius_label.setText(f"{radius_meters:.1f}m")
    
    def update_backward_radius(self, value):
        radius_meters = value / 10.0  # Konvertiere von 0.1m-Schritten zu Metern
        self.player.sectors["backward"].params.max_radius_meters = radius_meters
        self.player.sectors["backward"].update_path()
        self.backward_radius_label.setText(f"{radius_meters:.1f}m")
    
    def accept(self):
        # Speichere die Änderungen
        self.player.label = self.label_edit.text()
        super().accept() 