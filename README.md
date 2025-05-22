# Volleyball Strategie Manager

Eine interaktive Desktop‑Anwendung zur Visualisierung und Verwaltung von Volleyball‑Angriffs‑ und Abwehrformationen. Mit PySide6 gezeichnetem Spielfeld, bewegbaren Spielern, Annahmezonen und automatischer Einraster‑Funktion.

## Inhaltsverzeichnis

1. [Features](#features)
2. [Installation](#installation)
3. [Projektstruktur](#projektstruktur)
4. [Bedienung](#bedienung)
   - [Spielfeld und Spieler](#spielfeld-und-spieler)
   - [Kontextmenüs](#kontextmenüs)
   - [Annahmezonen](#annahmezonen)
   - [Formationen speichern und laden](#formationen-speichern-und-laden)
   - [Snap‑To‑Funktion](#snap‑to‑funktion)
5. [Module im Überblick](#module-im-überblick)
6. [License](#license)

## Features

- **Interaktives Spielfeld**: Volleyball‑Feld mit Netz, Angriffs‑ und Verteidigungslinien.
- **Spielerbewegung**: Spieler per Drag & Drop verschiebbar, mit dynamischem Schlagschatten.
- **Annahmezonen**: Rechteckige Zonen pro Spieler per Linksklick & Ziehen erstellen und speichern.
- **Kontextmenüs**:
  - Spieler: Name bearbeiten, Zone hinzufügen oder alle Zonen entfernen.
  - Zonen: Farbe anpassen oder löschen (werden bei Ballbewegung ausgeblendet).
- **Formationsverwaltung**: Speichern, Laden, Umbenennen und Löschen von Formationen.
- **Team‑Panel**: Speichern und Auswahl vordefinierter Spielernamen.
- **Interpolate & Snap**: Automatische Positionsinterpolation basierend auf geladenen Formationen und Einraster bei Annäherung an gespeicherte Ballposition.

## Installation

### Desktop-Version

1. Python 3.8+ installieren
2. Abhängigkeiten installieren:
   ```bash
   pip install PySide6
   ```
3. Projekt klonen und in das Verzeichnis wechseln:
   ```bash
   git clone <repo-url>
   cd VolleyballStrategieManager
   ```
4. Anwendung starten:
   ```bash
   python main.py
   ```

### Webserver-Version
1. Python 3.8+ installieren
2. Abhängigkeiten installieren:
```bash
pip install Flask
```
3. Server starten:
```bash
python webapp/app.py
```
4. Aufruf im Browser unter http://localhost:5000
### WebAssembly-Build
1. Emscripten und die Qt-for-Python WebAssembly-Pakete installieren.
2. Mit `pyside6-project` die Projektdateien erstellen und `pyside6-embed` ausführen, um die `.wasm`-Version zu erzeugen.
3. Im Build-Ordner `python -m http.server` starten und die generierte `index.html` im Browser öffnen.



## Projektstruktur

```
VolleyballStrategieManager/
├── main.py                       # Einstiegspunkt der Anwendung
├── components/                  
│   ├── player_item.py            # Spieler‑Klasse, Drag & Drop, Zonen, Kontextmenü
│   ├── ball_item.py              # Ball‑Klasse mit Bewegungsbegrenzung
│   └── formation_marker_item.py  # Marker für gespeicherte Ball‑Positionen
├── sectors/                     
│   └── attack_sector.py          # Angriff-Sektor‑Visualisierung
├── volleyball_field.py           # Spielfeld‑Rendering
├── defensive_positions_panel.py  # Panel zur Verwaltung und Auswahl von Formationen
├── team_panel.py                 # Panel zum Speichern/Laden von Team‑Namen
├── interpolation.py              # Hilfsfunktionen zur Positionsinterpolation
└── README.md                     # Dokumentation
```

## Bedienung

### Spielfeld und Spieler
- **Bewegen**: Linksklick & Ziehen auf einen Spieler.  
- **Schlagschatten**: Dynamisch sichtbar, wenn sich der Ball innerhalb 1 Meter vom Netz befindet.

### Kontextmenüs
- **Spieler per Rechtsklick**:
  - `Name bearbeiten`: Öffnet Dialog zum Eingeben eines neuen Spielernamens.
  - `Zone hinzufügen`: Aktiviert Zeichenmodus für Annahmezone.
  - `Zonen löschen`: Entfernt alle Annahmezonen dieses Spielers.
- **Zonen**: Rechtsklick öffnet Farbwahl („Zone bearbeiten“) oder Löschen.

### Annahmezonen
1. Rechtsklick auf Spieler → **Zone hinzufügen**.  
2. Linksklick & Ziehen: Rechteck auf Spielfeld aufziehen.  
3. Loslassen öffnet Farbwahl, halbtransparente Zone wird angelegt und im Panel gespeichert.

### Formationen speichern und laden
- Im **Defensive Positions Panel** links:
  - `Stellung speichern`: Vergib Namen, speichere Ball‑Koordinate, Spieler‑Offsets und Zonen.  
  - Rechtsklick auf Listeneintrag: Umbenennen oder Löschen.
  - Klick auf Eintrag: Formation anwenden (Ball & Spieler‑Positionen, Zonen zeichnen).

### Snap‑To‑Funktion
- Beim Ziehen des Balls rastet dieser ab 15 Pixel Abstand an die nächste gespeicherte Ball‑Position ein und lädt automatisch die Formation.

## Module im Überblick

- **main.py**: Initialisiert Szene, View, Panels und verbindet Signale.  
- **components/player_item.py**: Erbt von `DraggableEllipse`, verwaltet Spieleranzeige, Zonen und Kontextmenüs.  
- **components/ball_item.py**: `QGraphicsObject` mit Bewegungsgrenzen und Signal `positionChanged`.  
- **sectors/attack_sector.py**: Zeichnet den rot‑gelben Angriffssektor um den Ball.  
- **volleyball_field.py**: Hintergrund‑Spielfeld mit Netz und Linien.  
- **defensive_positions_panel.py**: Qt‑Widget, das Formationen listet und Speichern/Laden ermöglicht.  
- **team_panel.py**: Qt‑Widget zur Verwaltung von Teams und Spielernamen.  
- **interpolation.py**: Logik zur Positionsinterpolation zwischen Formationen.

## License

Dieses Projekt steht unter der MIT-Lizenz. Weitere Details siehe LICENSE-Datei. 