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
        # Aktuell ausgewählte Formation (Index)
        self.current_index = None
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
            with open("formations.json", "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # loaded is a list of dicts
                # Stelle sicher, dass jede Formation eine 'zones'-Liste hat
                self.formations = loaded
                for form in self.formations:
                    form.setdefault('zones', [])
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
            # Callback liefert (ball_center, offsets_list, zones)
            ball_center, offsets_list, zones = self.get_formation_callback()
        else:
            # Fallback ohne Zonen
            ball_center, offsets_list, zones = ( (100, 200), [], [] )

        # Convert formation to dict including zones
        formation_dict = {
            "name": name,
            "ball": [ball_center[0], ball_center[1]],
            "offsets": [[off[0], off[1]] for off in offsets_list],
            "zones": zones
        }
        self.formations.append(formation_dict)
        ball = formation_dict["ball"]
        ball_meters = (round(ball[0] * self.scale_factor, 2), round(ball[1] * self.scale_factor, 2))
        self.positions_list.addItem(f"Stellung: {name} - Ball {ball_meters}")
        self.save_formations()
        
    def on_item_clicked(self, item):
        idx = self.positions_list.row(item)
        if 0 <= idx < len(self.formations):
            # Merke aktuellen Index für Zonenupdates
            self.current_index = idx
            form = self.formations[idx]
            # Emit formation als Tuple: (Ball, Offsets, Zones)
            ball = tuple(form["ball"])
            offsets = [tuple(off) for off in form["offsets"]]
            zones = form.get('zones', [])
            self.formationSelected.emit((ball, offsets, zones))

    def show_context_menu(self, position):
        # Hole das Item an dieser Position
        item = self.positions_list.itemAt(position)
        if item is None:
            return
        # Kontextmenü: Umbenennen und Löschen
        context_menu = QMenu(self)
        rename_action = context_menu.addAction("Umbenennen...")
        delete_action = context_menu.addAction("Weg damit")
        action = context_menu.exec(self.positions_list.mapToGlobal(position))
        if action == rename_action:
            self.rename_formation(item)
        elif action == delete_action:
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

    def rename_formation(self, item):
        """
        Ermöglicht Umbenennen eines gespeicherten Formations-Namens per Dialog.
        """
        idx = self.positions_list.row(item)
        old_name = self.formations[idx]['name']
        new_name, ok = QInputDialog.getText(self, "Umbenennen", f"Geben Sie neuen Namen für '{old_name}' ein:")
        if not ok or not new_name:
            return
        # Aktualisiere Name in Daten und Liste
        self.formations[idx]['name'] = new_name
        ball = self.formations[idx]['ball']
        ball_meters = (round(ball[0] * self.scale_factor, 2), round(ball[1] * self.scale_factor, 2))
        item.setText(f"Stellung: {new_name} - Ball {ball_meters}")
        # Speichere Datei und signalisiere Änderung
        self.save_formations()

    def update_zone(self, player_index, rect, color):
        """
        Speichert eine Annahmezone für den gegebenen Spieler in der aktuellen Formation.
        """
        if self.current_index is None:
            return
        zones_list = self.formations[self.current_index].setdefault('zones', [])
        # Erstelle Eintrag und füge immer neu hinzu (mehrfach-Zonen)
        entry = {
            'player_index': player_index,
            'rect': [rect.x(), rect.y(), rect.width(), rect.height()],
            'color': [color.red(), color.green(), color.blue(), color.alpha()]
        }
        zones_list.append(entry)
        # Persistiere Änderungen
        self.save_formations()

    def delete_zone_entry(self, player_index, rect_vals, color_vals):
        """
        Entfernt eine gespeicherte Annahmezone aus der aktuellen Formation und speichert.
        rect_vals: [x,y,width,height], color_vals: [r,g,b,a]
        """
        if self.current_index is None:
            return
        zones_list = self.formations[self.current_index].get('zones', [])
        # Finde und entferne die erste passende Zone
        for zone in list(zones_list):
            if zone.get('player_index') == player_index and zone.get('rect') == rect_vals and zone.get('color') == color_vals:
                zones_list.remove(zone)
                break
        # Speichere aktualisierte Formationen
        self.save_formations()
