from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class DefensivePositionsPanel(QWidget):
    # Emit the selected formation: a tuple (ball_position, list_of_player_offsets)
    formationSelected = pyqtSignal(tuple)
    
    def __init__(self, get_formation_callback=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)  # adjust as needed
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.save_button = QPushButton("Stellung speichern", self)
        layout.addWidget(self.save_button)
        
        self.positions_list = QListWidget(self)
        layout.addWidget(self.positions_list)
        
        # Store formations; each is a tuple: (ball_position, [offsets])
        self.formations = []
        self.get_formation_callback = get_formation_callback
        
        self.save_button.clicked.connect(self.save_current_formation)
        self.positions_list.itemClicked.connect(self.on_item_clicked)

    def save_current_formation(self):
        if self.get_formation_callback:
            formation = self.get_formation_callback()  # (ball_center, offsets_list)
        else:
            formation = ((100, 200), [])  # dummy formation
        self.formations.append(formation)
        self.positions_list.addItem(f"Stellung: Ball {formation[0]}")
        
    def on_item_clicked(self, item):
        index = self.positions_list.row(item)
        if 0 <= index < len(self.formations):
            formation = self.formations[index]
            print("Abgerufene Stellung:", formation)
            self.formationSelected.emit(formation)
