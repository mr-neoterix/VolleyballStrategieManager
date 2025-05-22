import json  # Importiert das json-Modul für die Arbeit mit JSON-Daten.
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QInputDialog, QMenu  # Importiert notwendige Widgets von PyQt6 für die GUI.
from PySide6.QtCore import Qt, Signal  # Importiert Qt-Kernfunktionalitäten und das Signal-System von PyQt6.

class TeamPanel(QWidget):  # Definiert eine Klasse für das Panel zur Teamverwaltung, die von QWidget erbt.
    """
    Panel zur Verwaltung von Teams: Speichern, Laden und Auswählen.
    Persistenz in teams.json.
    """
    teamSelected = Signal(list)   # Definiert ein Signal, das ausgelöst wird, wenn ein Team ausgewählt wird und die Spielerliste sendet.
    # Signal bei Änderungen an der Teams-Liste, um die Änderungen zu speichern.
    teamsChanged = Signal(list)  # Definiert ein Signal, das bei Änderungen an der Teamliste ausgelöst wird.

    def __init__(self, get_names_callback=None, parent=None): # get_names_callback ist eine Funktion, die die Namen der Spieler ausliest.
        super().__init__(parent)  # Ruft den Konstruktor der Basisklasse QWidget auf.
        self.get_names_callback = get_names_callback  # Speichert die Callback-Funktion zum Abrufen der Spielernamen.
        self.teams = []  # Initialisiert eine leere Liste zur Speicherung der Teams (jedes Team als Diktionär: {'name': str, 'player_names': list}).

        self.setFixedWidth(250) # Setzt die feste Breite des Panels.
        layout = QVBoxLayout(self)  # Erstellt ein vertikales Box-Layout für dieses Widget.
        layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Richtet die Elemente im Layout oben aus.

        self.save_button = QPushButton("Team speichern", self)   # Erstellt einen Knopf zum Speichern des aktuellen Teams.
        layout.addWidget(self.save_button)  # Fügt den Knopf zum Layout hinzu.

        self.team_list = QListWidget(self)   # Erstellt eine Listenansicht für die gespeicherten Teams.
        self.team_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # Ermöglicht ein benutzerdefiniertes Kontextmenü für die Liste.
        layout.addWidget(self.team_list) # Fügt die Liste der Teams zum Layout hinzu.

        
        self.save_button.clicked.connect(self.save_current_team) # Verbindet das Klick-Signal des Speicherknopfs mit der Methode save_current_team.
        self.team_list.itemClicked.connect(self.on_item_clicked)  # Verbindet das Klick-Signal eines Listeneintrags mit der Methode on_item_clicked.
        self.team_list.customContextMenuRequested.connect(self.show_context_menu) # Verbindet das Signal für eine Kontextmenü-Anfrage mit der Methode show_context_menu.

        # Lädt die Teams aus teams.json.
        self.load_teams()   # Ruft die Methode zum Laden der Teams auf.

    def load_teams(self):  # Methode zum Laden der Teams aus einer JSON-Datei.
        """Lädt Teams aus teams.json und wählt das erste Team automatisch aus."""
        try:  # Beginnt einen try-Block für die Fehlerbehandlung beim Dateizugriff.
            with open("teams.json", "r", encoding="utf-8") as f: # Öffnet die Datei "teams.json" im Lesemodus mit UTF-8-Kodierung.
                loaded = json.load(f)  # Lädt die JSON-Daten aus der Datei.
                self.teams = loaded if isinstance(loaded, list) else []  # Weist die geladenen Teams der Instanzvariable zu, stellt sicher, dass es eine Liste ist.
        except (FileNotFoundError, json.JSONDecodeError):   # Behandelt den Fall, dass die Datei nicht gefunden wird oder einen JSON-Dekodierungsfehler enthält.
            self.teams = []  # Initialisiert die Teamliste als leer, wenn ein Fehler auftritt.

        self.team_list.clear()   # Leert die aktuelle Teamliste in der GUI.
        for team in self.teams:  # Iteriert über jedes geladene Team.
            self.team_list.addItem(team['name'])  # Fügt den Namen des Teams zur Listenansicht hinzu.

    
        self.teamsChanged.emit(self.teams)  # Löst das Signal teamsChanged aus, um über die geladenen Teams zu informieren.
        if self.teams:  # Überprüft, ob Teams geladen wurden.
            self.team_list.setCurrentRow(0)  # Wählt das erste Team in der Liste standardmäßig aus.
            self.on_item_clicked(self.team_list.currentItem()) # Wenn ein Team ausgewählt wird, wird die on_item_clicked Funktion aufgerufen.

    def save_teams(self):  # Methode zum Speichern der aktuellen Teamliste in eine JSON-Datei.
        """Speichert die Teams-Liste in teams.json."""
        with open("teams.json", "w", encoding="utf-8") as f:  # Öffnet die Datei "teams.json" im Schreibmodus mit UTF-8-Kodierung.
            json.dump(self.teams, f, ensure_ascii=False, indent=2)  # Schreibt die Teamliste im JSON-Format in die Datei (mit Einrückung für Lesbarkeit).
        self.teamsChanged.emit(self.teams)  # Löst das Signal teamsChanged aus, um über die Änderungen zu informieren.

    def save_current_team(self):  # Methode zum Speichern des aktuell konfigurierten Teams.
        """Speichert das aktuelle Team unter einem neuen Namen."""
        name, ok = QInputDialog.getText(self, "Team speichern", "Geben Sie einen Namen für das Team ein:")  # Öffnet einen Dialog zur Eingabe des Teamnamens.
        if not ok or not name:  # Überprüft, ob der Dialog erfolgreich mit "OK" beendet wurde und ein Name eingegeben wurde.
            return  # Bricht ab, wenn nicht.
        player_names = self.get_names_callback() if self.get_names_callback else []  # Ruft die Spielernamen über die Callback-Funktion ab, falls vorhanden.
        entry = {'name': name, 'player_names': player_names}  # Erstellt ein Dictionary für das neue Team.
        self.teams.append(entry)  # Fügt das neue Team zur Liste der Teams hinzu.
        self.team_list.addItem(name)  # Fügt den Namen des neuen Teams zur Listenansicht hinzu.
        self.save_teams()   # Ruft die Methode zum Speichern aller Teams auf.

    def on_item_clicked(self, item):  # Methode, die aufgerufen wird, wenn ein Element in der Teamliste angeklickt wird.
        """Sendet ein Signal für das ausgewählte Team mit den Spielernamen.""" # Englischer Kommentar übersetzt.
        idx = self.team_list.row(item)  # Ermittelt den Index des angeklickten Elements.
        if 0 <= idx < len(self.teams):  # Überprüft, ob der Index gültig ist.
            self.teamSelected.emit(self.teams[idx]['player_names'])  # Löst das Signal teamSelected mit den Namen der Spieler des ausgewählten Teams aus.

    def show_context_menu(self, pos):   # Methode zum Anzeigen eines Kontextmenüs für Listeneinträge.
        item = self.team_list.itemAt(pos)   # Holt das Listenelement an der angegebenen Mausposition.
        if not item:  # Überprüft, ob ein Element vorhanden ist.
            return  # Bricht ab, wenn kein Element an der Position ist.
        menu = QMenu(self)  # Erstellt ein neues Kontextmenü.
        delete_action = menu.addAction("Löschen")   # Fügt eine "Löschen"-Aktion zum Menü hinzu.
        action = menu.exec(self.team_list.mapToGlobal(pos))  # Zeigt das Kontextmenü an und wartet auf eine Aktion.
        if action == delete_action:  # Überprüft, ob die "Löschen"-Aktion ausgewählt wurde.
            self.delete_team(item)  # Ruft die Methode zum Löschen des Teams auf.

    def delete_team(self, item): # Löscht ein Team.
        idx = self.team_list.row(item)  # Ermittelt den Index des zu löschenden Elements.
        if 0 <= idx < len(self.teams):  # Überprüft, ob der Index gültig ist.
            del self.teams[idx]  # Löscht das Team aus der Liste der Teams.
            self.team_list.takeItem(idx)   # Entfernt das Element aus der Listenansicht.
            self.save_teams()   # Ruft die Methode zum Speichern aller Teams auf. 