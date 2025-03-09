import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QInputDialog, QMenu
from PyQt6.QtCore import Qt, pyqtSignal

class DefensivePositionsPanel(QWidget):
    # Emit the selected formation: a tuple (ball_position, list_of_player_offsets)
    formationSelected = pyqtSignal(tuple)
    # New signal to emit all formations when loaded or modified
    formationsChanged = pyqtSignal(list)
    
    def __init__(self, get_formation_callback=None, scale_factor=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)  # adjust as needed
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.save_button = QPushButton("Stellung speichern", self)
        layout.addWidget(self.save_button)
        
        self.positions_list = QListWidget(self)
        layout.addWidget(self.positions_list)
        
        # Enable context menu for the list widget
        self.positions_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.positions_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Store formations as a list of dicts: {"name": ..., "ball": [x, y], "offsets": [[x,y],...]}
        self.formations = []
        self.get_formation_callback = get_formation_callback
        # Use passed scale_factor or fallback (should always be provided from volleyball_field)
        self.scale_factor = scale_factor if scale_factor is not None else 0.01
        
        self.save_button.clicked.connect(self.save_current_formation)
        self.positions_list.itemClicked.connect(self.on_item_clicked)

        # Load previously saved formations
        self.load_formations()

    def load_formations(self):
        try:
            with open("formations.json", "r") as f:
                loaded = json.load(f)
                # loaded is a list of dicts
                self.formations = loaded
                for form in loaded:
                    ball = form["ball"]
                    ball_meters = (round(ball[0] * self.scale_factor, 2), round(ball[1] * self.scale_factor, 2))
                    self.positions_list.addItem(f"Stellung: {form['name']} - Ball {ball_meters}")
                
                # Emit all loaded formations
                self.formationsChanged.emit(self.formations)
        except FileNotFoundError:
            pass

    def save_formations(self):
        with open("formations.json", "w") as f:
            json.dump(self.formations, f)
        # Emit all formations after saving
        self.formationsChanged.emit(self.formations)

    def save_current_formation(self):
        # Ask for formation name
        name, ok = QInputDialog.getText(self, "Speichern", "Geben Sie einen Namen für die Stellung ein:")
        if not ok:
            return
        if self.get_formation_callback:
            formation = self.get_formation_callback()  # (ball_center, offsets_list)
        else:
            formation = ((100, 200), [])  # dummy formation

        # Convert formation to dict {"name": name, "ball": [x,y], "offsets": [[x,y],...]}
        formation_dict = {
            "name": name,
            "ball": [formation[0][0], formation[0][1]],
            "offsets": [[off[0], off[1]] for off in formation[1]]
        }
        self.formations.append(formation_dict)
        ball = formation_dict["ball"]
        ball_meters = (round(ball[0] * self.scale_factor, 2), round(ball[1] * self.scale_factor, 2))
        self.positions_list.addItem(f"Stellung: {name} - Ball {ball_meters}")
        self.save_formations()
        
    def on_item_clicked(self, item):
        index = self.positions_list.row(item)
        if 0 <= index < len(self.formations):
            form = self.formations[index]
            print("Abgerufene Stellung:", form)
            # Emit formation as tuple: (ball as tuple, offsets as list of tuples)
            self.formationSelected.emit((tuple(form["ball"]), [tuple(off) for off in form["offsets"]]))

    def show_context_menu(self, position):
        # Get the item at the position
        item = self.positions_list.itemAt(position)
        if item is None:
            return
            
        # Create context menu
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Weg damit")
        
        # Show context menu and get selected action
        action = context_menu.exec(self.positions_list.mapToGlobal(position))
        
        # Handle the selected action
        if action == delete_action:
            self.delete_formation(item)
    
    def delete_formation(self, item):
        index = self.positions_list.row(item)
        if 0 <= index < len(self.formations):
            # Remove from formations list
            del self.formations[index]
            # Remove from list widget
            self.positions_list.takeItem(index)
            # Save changes to file
            self.save_formations()
            # This will also emit formationsChanged signal via save_formations
