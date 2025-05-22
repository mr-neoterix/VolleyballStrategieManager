import json  # Importiert das json-Modul für die Arbeit mit JSON-Daten.
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QInputDialog, QMenu  # Importiert notwendige Widgets von PyQt6 für die GUI.
from PySide6.QtCore import Qt, Signal  # Importiert Qt-Kernfunktionalitäten und das Signal-System von PyQt6.

class DefensivePositionsPanel(QWidget):  # Definiert eine Klasse für das Panel der Defensivpositionen, die von QWidget erbt.
    # Sendet die ausgewählte Formation: ein Tupel (Ballposition, Liste von Spieler-Offsets)
    formationSelected = Signal(tuple)  # Definiert ein Signal, das ausgelöst wird, wenn eine Formation ausgewählt wird.
    # Neues Signal, um alle Formationen zu senden, wenn sie geladen oder geändert wurden
    formationsChanged = Signal(list)  # Definiert ein Signal, das bei Änderungen an den Formationen ausgelöst wird.
    
    def __init__(self, get_formation_callback=None, scale_factor=None, parent=None):  # Konstruktor der Klasse.
        super().__init__(parent)  # Ruft den Konstruktor der Basisklasse QWidget auf.
        # Aktuell ausgewählte Formation (Index)
        self.current_index = None  # Initialisiert den Index der aktuell ausgewählten Formation.
        self.setFixedWidth(250)  # Setzt eine feste Breite für das Panel (ggf. anpassen).
        layout = QVBoxLayout(self)  # Erstellt ein vertikales Box-Layout für dieses Widget.
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Richtet die Elemente im Layout oben aus.
        
        self.save_button = QPushButton("Stellung speichern", self)  # Erstellt einen Knopf zum Speichern der aktuellen Stellung.
        layout.addWidget(self.save_button)  # Fügt den Knopf zum Layout hinzu.
        
        self.positions_list = QListWidget(self)  # Erstellt eine Listenansicht für die gespeicherten Positionen.
        layout.addWidget(self.positions_list)  # Fügt die Listenansicht zum Layout hinzu.
        
        # Kontextmenü für das Listen-Widget aktivieren
        self.positions_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # Ermöglicht ein benutzerdefiniertes Kontextmenü für die Liste.
        self.positions_list.customContextMenuRequested.connect(self.show_context_menu)  # Verbindet das Signal für eine Kontextmenü-Anfrage mit der Methode show_context_menu.
        
        # Formationen als Liste von Dictionaries speichern: {"name": ..., "ball": [x, y], "offsets": [[x,y],...]}
        self.formations = []  # Initialisiert eine leere Liste zur Speicherung der Formationen.
        self.get_formation_callback = get_formation_callback  # Speichert die Callback-Funktion, um Formationsdaten abzurufen.
        # Übergebenen scale_factor verwenden oder auf Standardwert zurückgreifen (sollte immer von volleyball_field bereitgestellt werden)
        self.scale_factor = scale_factor if scale_factor is not None else 0.01  # Setzt den Skalierungsfaktor, Standardwert ist 0.01.
        
        self.save_button.clicked.connect(self.save_current_formation)  # Verbindet das Klick-Signal des Speicherknopfs mit der Methode save_current_formation.
        self.positions_list.itemClicked.connect(self.on_item_clicked)  # Verbindet das Klick-Signal eines Listeneintrags mit der Methode on_item_clicked.

        # Zuvor gespeicherte Formationen laden
        self.load_formations()  # Ruft die Methode zum Laden der Formationen auf.

    def load_formations(self):  # Methode zum Laden der Formationen aus einer Datei.
        try:  # Beginnt einen try-Block für die Fehlerbehandlung beim Dateizugriff.
            with open("formations.json", "r", encoding="utf-8") as f:  # Öffnet die Datei "formations.json" im Lesemodus mit UTF-8-Kodierung.
                loaded = json.load(f)  # Lädt die JSON-Daten aus der Datei.
                # "loaded" ist eine Liste von Dictionaries
                # Stelle sicher, dass jede Formation eine 'zones'-Liste hat
                self.formations = loaded  # Weist die geladenen Formationen der Instanzvariable zu.
                for form in self.formations:  # Iteriert über jede geladene Formation.
                    form.setdefault('zones', [])  # Stellt sicher, dass jede Formation einen 'zones'-Schlüssel hat; fügt ihn hinzu, falls nicht vorhanden.
                for form in loaded:  # Iteriert erneut über die geladenen Formationen, um sie der Liste hinzuzufügen.
                    ball = form["ball"]  # Holt die Ballposition aus der Formation.
                    ball_meters = (round(ball[0] * self.scale_factor, 2), round(ball[1] * self.scale_factor, 2))  # Rechnet die Ballkoordinaten in Meter um.
                    self.positions_list.addItem(f"Stellung: {form['name']} - Ball {ball_meters}")  # Fügt einen Eintrag zur Positionsliste hinzu.
                
                # Alle geladenen Formationen senden
                self.formationsChanged.emit(self.formations)  # Löst das Signal formationsChanged aus, um über die geladenen Formationen zu informieren.
        except FileNotFoundError:  # Behandelt den Fall, dass die Datei "formations.json" nicht gefunden wird.
            pass  # Macht nichts, wenn die Datei nicht existiert (z.B. beim ersten Start).

    def save_formations(self):  # Methode zum Speichern der Formationen in eine Datei.
        with open("formations.json", "w") as f:  # Öffnet die Datei "formations.json" im Schreibmodus.
            json.dump(self.formations, f)  # Schreibt die aktuellen Formationen im JSON-Format in die Datei.
        # Alle Formationen nach dem Speichern senden
        self.formationsChanged.emit(self.formations)  # Löst das Signal formationsChanged aus, um über die Änderungen zu informieren.

    def save_current_formation(self):  # Methode zum Speichern der aktuell definierten Formation.
        # Nach Formationsnamen fragen
        name, ok = QInputDialog.getText(self, "Speichern", "Geben Sie einen Namen für die Stellung ein:")  # Öffnet einen Dialog zur Eingabe des Formationsnamens.
        if not ok:  # Überprüft, ob der Dialog erfolgreich mit "OK" beendet wurde.
            return  # Bricht ab, wenn der Dialog nicht mit "OK" beendet wurde.
        if self.get_formation_callback:  # Überprüft, ob eine Callback-Funktion zum Abrufen der Formationsdaten vorhanden ist.
            # Callback liefert (ball_center, offsets_list, zones)
            ball_center, offsets_list, zones = self.get_formation_callback()  # Ruft die Formationsdaten über die Callback-Funktion ab.
        else:  # Falls keine Callback-Funktion vorhanden ist.
            # Fallback ohne Zonen
            ball_center, offsets_list, zones = ( (100, 200), [], [] )  # Verwendet Standardwerte für die Formationsdaten.

        # Formation als Dictionary konvertieren, inklusive Zonen
        formation_dict = {  # Erstellt ein Dictionary, das die Formation repräsentiert.
            "name": name,  # Speichert den Namen der Formation.
            "ball": [ball_center[0], ball_center[1]],  # Speichert die Ballposition.
            "offsets": [[off[0], off[1]] for off in offsets_list],  # Speichert die Spieler-Offsets.
            "zones": zones  # Speichert die Zoneninformationen.
        }
        self.formations.append(formation_dict)  # Fügt das neue Formations-Dictionary zur Liste der Formationen hinzu.
        ball = formation_dict["ball"]  # Holt die Ballposition aus dem Dictionary.
        ball_meters = (round(ball[0] * self.scale_factor, 2), round(ball[1] * self.scale_factor, 2))  # Rechnet die Ballkoordinaten in Meter um.
        self.positions_list.addItem(f"Stellung: {name} - Ball {ball_meters}")  # Fügt einen Eintrag für die neue Formation zur Positionsliste hinzu.
        self.save_formations()  # Ruft die Methode zum Speichern aller Formationen auf.
        
    def on_item_clicked(self, item):  # Methode, die aufgerufen wird, wenn ein Element in der Positionsliste angeklickt wird.
        idx = self.positions_list.row(item)  # Ermittelt den Index des angeklickten Elements.
        if 0 <= idx < len(self.formations):  # Überprüft, ob der Index gültig ist.
            # Aktuellen Index für Zonenupdates merken
            self.current_index = idx  # Speichert den Index der ausgewählten Formation.
            form = self.formations[idx]  # Holt die ausgewählte Formation aus der Liste.
            # Formation als Tupel senden: (Ball, Offsets, Zonen)
            ball = tuple(form["ball"])  # Konvertiert die Ballposition in ein Tupel.
            offsets = [tuple(off) for off in form["offsets"]]  # Konvertiert die Spieler-Offsets in eine Liste von Tupeln.
            zones = form.get('zones', [])  # Holt die Zoneninformationen; Standard ist eine leere Liste.
            self.formationSelected.emit((ball, offsets, zones))  # Löst das Signal formationSelected mit den Daten der ausgewählten Formation aus.

    def show_context_menu(self, position):  # Methode zum Anzeigen eines Kontextmenüs für Listeneinträge.
        # Das Item an dieser Position holen
        item = self.positions_list.itemAt(position)  # Holt das Listenelement an der angegebenen Mausposition.
        if item is None:  # Überprüft, ob ein Element vorhanden ist.
            return  # Bricht ab, wenn kein Element an der Position ist.
        # Kontextmenü: Umbenennen und Löschen
        context_menu = QMenu(self)  # Erstellt ein neues Kontextmenü.
        rename_action = context_menu.addAction("Umbenennen...")  # Fügt eine "Umbenennen"-Aktion zum Menü hinzu.
        delete_action = context_menu.addAction("Weg damit")  # Fügt eine "Löschen"-Aktion zum Menü hinzu (humorvoll formuliert).
        action = context_menu.exec(self.positions_list.mapToGlobal(position))  # Zeigt das Kontextmenü an und wartet auf eine Aktion.
        if action == rename_action:  # Überprüft, ob die "Umbenennen"-Aktion ausgewählt wurde.
            self.rename_formation(item)  # Ruft die Methode zum Umbenennen der Formation auf.
        elif action == delete_action:  # Überprüft, ob die "Löschen"-Aktion ausgewählt wurde.
            self.delete_formation(item)  # Ruft die Methode zum Löschen der Formation auf.
    
    def delete_formation(self, item):  # Methode zum Löschen einer Formation.
        index = self.positions_list.row(item)  # Ermittelt den Index des zu löschenden Elements.
        if 0 <= index < len(self.formations):  # Überprüft, ob der Index gültig ist.
            # Aus der Formationsliste entfernen
            del self.formations[index]  # Löscht die Formation aus der Liste der Formationen.
            # Aus dem Listen-Widget entfernen
            self.positions_list.takeItem(index)  # Entfernt das Element aus der Listenansicht.
            # Änderungen in Datei speichern
            self.save_formations()  # Ruft die Methode zum Speichern aller Formationen auf.
            # Dies löst auch das formationsChanged-Signal über save_formations aus

    def rename_formation(self, item):  # Methode zum Umbenennen einer Formation.
        """
        Ermöglicht Umbenennen eines gespeicherten Formations-Namens per Dialog.
        """
        idx = self.positions_list.row(item)  # Ermittelt den Index des umzubenennenden Elements.
        old_name = self.formations[idx]['name']  # Holt den alten Namen der Formation.
        new_name, ok = QInputDialog.getText(self, "Umbenennen", f"Geben Sie neuen Namen für '{old_name}' ein:")  # Öffnet einen Dialog zur Eingabe des neuen Namens.
        if not ok or not new_name:  # Überprüft, ob der Dialog erfolgreich beendet wurde und ein Name eingegeben wurde.
            return  # Bricht ab, wenn nicht.
        # Name in Daten und Liste aktualisieren
        self.formations[idx]['name'] = new_name  # Aktualisiert den Namen in der Formationsliste.
        ball = self.formations[idx]['ball']  # Holt die Ballposition.
        ball_meters = (round(ball[0] * self.scale_factor, 2), round(ball[1] * self.scale_factor, 2))  # Rechnet die Ballkoordinaten in Meter um.
        item.setText(f"Stellung: {new_name} - Ball {ball_meters}")  # Aktualisiert den Text des Listeneintrags.
        # Datei speichern und Änderung signalisieren
        self.save_formations()  # Ruft die Methode zum Speichern aller Formationen auf.

    def update_zone(self, player_index, rect, color):  # Methode zum Aktualisieren oder Hinzufügen einer Zone für einen Spieler.
        """
        Speichert eine Annahmezone für den gegebenen Spieler in der aktuellen Formation.
        """
        if self.current_index is None:  # Überprüft, ob eine Formation ausgewählt ist.
            return  # Bricht ab, wenn keine Formation ausgewählt ist.
        zones_list = self.formations[self.current_index].setdefault('zones', [])  # Holt die Zonenliste der aktuellen Formation oder erstellt eine neue.
        # Eintrag erstellen und immer neu hinzufügen (mehrfach-Zonen)
        entry = {  # Erstellt ein Dictionary für den Zoneneintrag.
            'player_index': player_index,  # Speichert den Index des Spielers.
            'rect': [rect.x(), rect.y(), rect.width(), rect.height()],  # Speichert die Rechteckkoordinaten der Zone.
            'color': [color.red(), color.green(), color.blue(), color.alpha()]  # Speichert die Farbe der Zone.
        }
        zones_list.append(entry)  # Fügt den neuen Zoneneintrag zur Liste hinzu.
        # Änderungen persistieren
        self.save_formations()  # Ruft die Methode zum Speichern aller Formationen auf.

    def delete_zone_entry(self, player_index, rect_vals, color_vals):  # Methode zum Löschen eines spezifischen Zoneneintrags.
        """
        Entfernt eine gespeicherte Annahmezone aus der aktuellen Formation und speichert.
        rect_vals: [x,y,width,height], color_vals: [r,g,b,a]
        """
        if self.current_index is None:  # Überprüft, ob eine Formation ausgewählt ist.
            return  # Bricht ab, wenn keine Formation ausgewählt ist.
        zones_list = self.formations[self.current_index].get('zones', [])  # Holt die Zonenliste der aktuellen Formation.
        # Die erste passende Zone finden und entfernen
        for zone in list(zones_list):  # Iteriert über eine Kopie der Zonenliste, um sie während der Iteration modifizieren zu können.
            if zone.get('player_index') == player_index and zone.get('rect') == rect_vals and zone.get('color') == color_vals:  # Überprüft, ob der Zoneneintrag den Kriterien entspricht.
                zones_list.remove(zone)  # Entfernt den passenden Zoneneintrag.
                break  # Beendet die Schleife, nachdem der Eintrag entfernt wurde.
        # Aktualisierte Formationen speichern
        self.save_formations()  # Ruft die Methode zum Speichern aller Formationen auf.
