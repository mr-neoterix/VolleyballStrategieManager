import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QInputDialog, QMenu
from PyQt6.QtCore import Qt, pyqtSignal

class TeamPanel(QWidget):
    """
    Panel zur Verwaltung von Teams: Speichern, Laden und Auswählen.
    Persistenz in teams.json.
    """
    # Signal mit der Liste der Spielernamen eines ausgewählten Teams
    teamSelected = pyqtSignal(list)
    # Signal bei Änderungen an der Teams-Liste
    teamsChanged = pyqtSignal(list)

    def __init__(self, get_names_callback=None, parent=None):
        super().__init__(parent)
        self.get_names_callback = get_names_callback
        self.teams = []  # Liste von Dicts: {'name': str, 'player_names': [str, ...]}

        self.setFixedWidth(250)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.save_button = QPushButton("Team speichern", self)
        layout.addWidget(self.save_button)

        self.team_list = QListWidget(self)
        self.team_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.team_list)

        # Events
        self.save_button.clicked.connect(self.save_current_team)
        self.team_list.itemClicked.connect(self.on_item_clicked)
        self.team_list.customContextMenuRequested.connect(self.show_context_menu)

        # Lade vorhandene Teams
        self.load_teams()

    def load_teams(self):
        """Lädt Teams aus teams.json und wählt das erste Team automatisch aus."""
        try:
            with open("teams.json", "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.teams = loaded if isinstance(loaded, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            self.teams = []

        self.team_list.clear()
        for team in self.teams:
            self.team_list.addItem(team['name'])

        # Signal und Standardauswahl
        self.teamsChanged.emit(self.teams)
        if self.teams:
            self.team_list.setCurrentRow(0)
            self.on_item_clicked(self.team_list.currentItem())

    def save_teams(self):
        """Speichert die Teams-Liste in teams.json."""
        with open("teams.json", "w", encoding="utf-8") as f:
            json.dump(self.teams, f, ensure_ascii=False, indent=2)
        self.teamsChanged.emit(self.teams)

    def save_current_team(self):
        """Speichert das aktuelle Team unter einem neuen Namen."""
        name, ok = QInputDialog.getText(self, "Team speichern", "Geben Sie einen Namen für das Team ein:")
        if not ok or not name:
            return
        player_names = self.get_names_callback() if self.get_names_callback else []
        entry = {'name': name, 'player_names': player_names}
        self.teams.append(entry)
        self.team_list.addItem(name)
        self.save_teams()

    def on_item_clicked(self, item):
        """Emit für ausgewähltes Team mit Spielernamen."""
        idx = self.team_list.row(item)
        if 0 <= idx < len(self.teams):
            self.teamSelected.emit(self.teams[idx]['player_names'])

    def show_context_menu(self, pos):
        item = self.team_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        delete_action = menu.addAction("Löschen")
        action = menu.exec(self.team_list.mapToGlobal(pos))
        if action == delete_action:
            self.delete_team(item)

    def delete_team(self, item):
        idx = self.team_list.row(item)
        if 0 <= idx < len(self.teams):
            del self.teams[idx]
            self.team_list.takeItem(idx)
            self.save_teams() 