# Volleyball Strategie Manager – Dokumentation

**Interaktive Desktop-Anwendung zur Visualisierung und Verwaltung von Volleyball-Angriffs- und Abwehrformationen**  
**Python 3.8+ · PyQt6**

---

## Inhaltsverzeichnis

- [Kurzreferat](#kurzreferat) ............................................... 3
- [1. Einleitung](#1-einleitung) ......................................... 4
  - [1.1. Themenwahl](#11-themenwahl) .......................... 4
  - [1.2. Zielstellung](#12-zielstellung) ..................... 4
  - [1.3. Motivation](#13-motivation) ........................ 4
- [2. Vorbetrachtung](#2-vorbetrachtung) ................................. 4
  - [2.1. Zeichnen des Volleyballfelds](#21-zeichnen-des-volleyballfelds) ... 4
  - [2.2. Evaluierung von PyQt6](#22-evaluierung-von-pyqt6) ........................ 5
- [3. Ergebnisse](#3-ergebnisse) ........................................... 7
  - [3.1. Grafische Benutzeroberfläche (GUI)](#31-grafische-benutzeroberflaeche-gui) ... 7
    - [3.1.1. Interaktives Spielfeld](#311-interaktives-spielfeld) ........ 7
    - [3.1.2. Spielerbewegung](#312-spielerbewegung) .................. 7
    - [3.1.3. Annahmezonen](#313-annahmezonen) ......................... 8
    - [3.1.4. Formationsverwaltung](#314-formationsverwaltung) ....... 8
    - [3.1.5. Kontextmenüs](#315-kontextmenues) ...................... 9
    - [3.1.6. Angriffssektor](#316-angriffssektor) ...................... 10
  - [3.2. Snap-To-Funktion](#32-snap-to-funktion) ....................... 10
  - [3.3. Team-Panel](#33-team-panel) ................................... 10
- [4. Installation](#4-installation) ...................................... 12
- [5. Projektstruktur](#5-projektstruktur) ................................ 13
- [6. Bedienung](#6-bedienung) ........................................... 14
  - [6.1. Spielfeld und Spieler](#61-spielfeld-und-spieler) .......... 14
  - [6.2. Kontextmenüs](#62-kontextmenues) ......................... 15
  - [6.3. Snap-To-Funktion](#63-snap-to-funktion) ................ 15
- [7. Module im Überblick](#7-module-im-uberblick) ....................... 16
- [8. License](#8-license) ................................................ 18

## Kurzreferat

Der **Volleyball Strategie Manager** ist eine interaktive Desktop-Anwendung zur Visualisierung und Verwaltung von Volleyball-Angriffs- und Abwehrformationen. Die Software bietet ein mit PyQt6 gezeichnetes Spielfeld, bewegbare Spieler, konfigurierbare Annahmezonen sowie eine automatische Einraster-Funktion beim Ziehen des Balls. Sie richtet sich an Trainer und Teams, die ihre taktischen Aufstellungen effizient planen und präsentieren möchten.

## 1. Einleitung

### 1.1. Themenwahl

In Volleyball spielen die Positionierung und taktische Aufstellung der Spieler eine zentrale Rolle. Häufig werden Formation und Laufwege auf Papier oder mit statischen Grafiken geplant, was zeitintensiv ist und wenig Flexibilität bietet. Mit dem Volleyball Strategie Manager wird erstmals eine interaktive Plattform bereitgestellt, mit der Formationen digital gezeichnet, variiert und direkt visuell geprüft werden können. Bälle können verschoben, Zonen definiert und ihre Auswirkungen in Echtzeit beobachtet werden, ohne mühsame Neuzeichnungen.

### 1.2. Zielstellung

Ziel der Anwendung ist es, eine intuitive Benutzeroberfläche zu bieten, mit der Formationen dynamisch erstellt, individuell angepasst, abgespeichert und jederzeit wieder aufgerufen werden können. Dabei stehen im Mittelpunkt:

- **Dynamisches Erstellen:** Neue Formationen können mit wenigen Klicks angelegt und Spieler per Drag-&-Drop platziert werden.
- **Visuelle Anpassung:** Annahme- und Angriffsbereiche können als frei konfigurierbare Zonen gezeichnet und später per Kontextmenü bearbeitet werden.
- **Speichern & Laden:** Jede Formation wird in einer JSON-Datenbank gespeichert und kann über einen eindeutigen Namen schnell abgerufen werden.

Im Training kann so zwischen verschiedenen Aufstellungen gewechselt werden, ohne dass umständlich Dokumente durchsucht werden müssen.

Das Feature wird von Jonas (Zuspieler, 25) genutzt, damit seine bevorzugten Spielzüge abgespeichert werden können.

### 1.3. Motivation

Der Bedarf an digitalen Hilfsmitteln im Volleyball ist hoch: Bei klassischen Taktiktafeln ist ein erneutes Zeichnen bei Änderungen erforderlich, und es wird keine direkte Interaktion geboten. Durch eine Softwarelösung wird die Zusammenarbeit im Team gefördert, das Teilen von Spielkonzepten erleichtert und Trainingsinhalte multimedial erfasst.

## 2. Vorbetrachtung

### 2.1. Zeichnen des Volleyballfelds

In der Vorentwicklung wurden verschiedene Ansätze geprüft, um das Volleyballfeld in Draufsicht (Vogelperspektive) darzustellen. Ein statisches Spielfeld wurde mithilfe von `QGraphicsRectItem` für die Spielfeldbegrenzungen und Mittellinien sowie `QGraphicsLineItem` für Netz und Seitenlinien aufgebaut. Spieler- und Ballmarkierungen wurden mit `QGraphicsEllipseItem` als einfache Kreise visualisiert.

Die Vogelperspektive ermöglicht eine klare zweidimensionale Darstellung, die das Platzieren von Spielern und Zonen vereinfacht. Auf den Einsatz komplexer Pfadobjekte wurde verzichtet, um die Performance hoch und den Implementierungsaufwand gering zu halten. Skalierung und Interaktion erfolgen über die eingebaute `QGraphicsView`-Funktionalität, die flüssige Ansichten bei unterschiedlichen Zoomstufen garantiert.

### 2.2. Evaluierung von PyQt6

PyQt6 bietet mit seiner `QGraphicsView`-Architektur nicht nur Zeichenfunktionen, sondern auch integriertes Event-Handling und Performance-Optimierungen für große Szenen. Das benötigte Echtzeit-Feedback beim Verschieben von Spielern wurde durch sofortige Neuzeichnungen realisiert, ohne dass merkliche Verzögerungen auftraten. Auch die Kombination aus `QPen` und `QBrush` für unterschiedliche Linienfarben und Flächenschattierungen deckt alle Anforderungen ab.

Daher wurde die Entscheidung getroffen, die Spielfeld-Rendering-Logik vollständig auf das Qt-Grafikframework zu stützen.

## 3. Ergebnisse

### 3.1. Grafische Benutzeroberfläche (GUI)

#### 3.1.1. Interaktives Spielfeld

Das Volleyball-Feld wird in einer `QGraphicsScene` in Vogelperspektive dargestellt. Für die Spielfeldbegrenzungen und Mittellinien werden `QGraphicsRectItem` eingesetzt, während Netz und Seitenlinien mit `QGraphicsLineItem` realisiert werden. Die Koordinaten werden so gewählt, dass ein reales Seitenverhältnis entsteht und die Farbwahl dem offiziellen Regelwerk entspricht. Über den Überhangbereich hinaus werden Spielfeldränder als zusätzliche Flächen angelegt, um Bewegungen nahe der Feldgrenzen korrekt darzustellen.

Die Skalierung und Ansicht erfolgen über die `QGraphicsView`, die bei Fensteränderungen automatisch an das Seitenverhältnis angepasst wird. Z-Werte (Layer) sorgen dafür, dass Netz, Feld und Spieler stets in der richtigen Render-Reihenfolge angezeigt werden. Ein Hintergrundgitter unterstützt die präzise Platzierung der Spieler.

#### 3.1.2. Spielerbewegung

Spieler werden als mit `QGraphicsEllipseItem` dargestellte Kreise konfiguriert und mit einem farbigen `QBrush` gefüllt. Das Verschieben erfolgt über Drag-&-Drop, wobei Maus-Ereignisse verarbeitet und neue Positionen in Echtzeit berechnet werden. Kollisionserkennung mit den Spielfeldrändern verhindert ein Verlassen des Feldes.

Ein Schatteneffekt wird durch ein leicht skaliertes, halbtransparentes Ellipse-Objekt hinter jedem Spieler erzeugt. Beim Loslassen der Maustaste wird über Signal-Slot-Verbindungen die neue Position gespeichert und alle abhängigen Elemente (Schatten, Zonen, Formationserkennung) aktualisiert.

Ein Blockschatten wird erzeugt, wenn sich ein Spieler innerhalb einer definierten Distanz (ca. 1 Meter) vom Netz befindet. In der Methode `updateShadow` wird hierfür ein `QPainterPath` erstellt, der als Kreisbogen um den Ball verläuft, und mit einem `QRadialGradient` gefüllt, dessen Transparenz mit zunehmender Entfernung vom Ball abnimmt. Dieser Schatten visualisiert das Abwehrpotential und hilft Trainern, Abwehrbereiche und Blockpositionen taktisch einzuschätzen.

#### 3.1.3. Annahmezonen

Annahmezonen werden über das Kontextmenü eines Spielers aktiviert. Im Zeichenmodus kann ein Rechteck aufgezogen werden, das nach Freigabe der Maustaste in ein `QGraphicsRectItem` mit transparenter Füllung und farblicher Kontur umgewandelt wird. Farben lassen sich über einen Farbwähler anpassen. Beim Laden einer Formation werden alle gespeicherten Zonen automatisch rekonstruiert und mit der Szene synchronisiert.

Eine dynamische Hervorhebung zeigt an, wenn sich der Ball innerhalb einer Zone befindet. Diese visuelle Rückmeldung hilft Trainern, taktische Deckungsbereiche zu bewerten.

#### 3.1.4. Formationsverwaltung

Das Defensive Positions Panel verwendet eine `QListView`, um alle gespeicherten Formationen darzustellen. Formationen werden in einer JSON-Datei abgelegt, die Ball-Koordinaten, Spieler-Offsets und Zonen-Daten enthält. Über Buttons können neue Formationen hinzugefügt, bestehende umbenannt oder gelöscht werden.

Beim Speichern wird geprüft, ob ein Name bereits vorhanden ist, und bei Konflikten eine Fehlermeldung angezeigt. Ein Klick auf eine Liste lädt die gewählte Formation, positioniert alle Elemente neu und aktualisiert die Szene. Alle Aktionen erfolgen asynchron, sodass die UI stets reaktionsfähig bleibt.

#### 3.1.5. Kontextmenüs

- **Spieler**:
  - `Name bearbeiten`: Öffnet einen Dialog zum Anpassen des Spielernamens.
  - `Zone hinzufügen`: Aktiviert den Zeichenmodus für Annahmezonen.
  - `Zonen löschen`: Entfernt alle Zonen des ausgewählten Spielers.
- **Zonen**:
  - `Farbe ändern`: Öffnet einen Farbwähler für Kontur- und Füllfarbe.
  - `Löschen`: Entfernt die ausgewählte Zone aus der Formation.

#### 3.1.6. Angriffssektor

Ein Angriffssektor wird durch die Klasse `AttackSector` in `sectors/attack_sector.py` bereitgestellt, welche von `BaseSector` erbt. In der Methode `update_path` wird ein `QPainterPath` erzeugt, der am Ballmittelpunkt startet und einen Bogen zur Netzlinie beschreibt. Der Radius des Bogens passt sich dynamisch an den Abstand des Balles zum unteren Spielfeldrand an. Zur visuellen Ausgestaltung werden zwei Gradienten kombiniert: Ein `QRadialGradient` erzeugt einen Farbverlauf von Rot (im Zentrum) zu Gelb (am Rand) und ein `QConicalGradient` fügt eine konische Farbschicht hinzu, um unterschiedliche Angriffswinkel darzustellen. Beide Gradienten werden auf ein temporäres `QPixmap` aufgetragen und mit einem Alpha-Wert von 0.5 versehen. Abschließend wird der resultierende `QBrush` mithilfe von `QTransform` an die korrekte Szene-Koordinate verschoben, um den sektoralen Bereich nahtlos über dem Spielfeld zu platzieren.

### 3.2. Snap-To-Funktion

Die Snap-To-Funktion basiert auf der Berechnung des euklidischen Abstands zwischen der aktuellen Ballposition und allen in der Datenbank gespeicherten Formationseinträgen. Sobald ein zuvor konfigurierter Schwellenwert unterschritten wird, wird die Ballposition automatisch auf die gespeicherte Koordinate gesetzt und die zugehörige Formation geladen. Eine kurze Animation mit `QPropertyAnimation` (Dauer: 200 ms, Ease-Out-Kurve) visualisiert das Einrasten, wodurch ein visuelles Feedback erzeugt wird.

Zusätzlich wird ein `QTimer` genutzt, um den Abstand in regelmäßigen Intervallen (z. B. 30 ms) neu zu prüfen, ohne dabei die UI-Performance zu beeinträchtigen. Um mehrfaches Triggern zu vermeiden, wird nach erfolgreichem Snap eine kurze Sperrzeit (Cooldown) von 500 ms aktiviert. Verschiedene Schwellenwerte (z. B. 10 – 20 Pixel) können in den Einstellungen angepasst werden, um auf unterschiedlichen Bildschirmauflösungen konsistente Rückmeldung zu gewährleisten.

Der Snap-Algorithmus verwendet intern Quadtrees zur effizienten Suche nach den nächsten gespeicherten Positionen, wodurch auch bei hunderten Formationen eine konstante Reaktionszeit gewährleistet ist.

### 3.3. Team-Panel

Das Team-Panel ist als `QListView` implementiert und dient der Verwaltung benannter Teams. Die Teamdaten werden in der Datei `teams.json` verwaltet, deren Struktur wie folgt aufgebaut ist:

```json
{
  "Team A": ["Spieler1", "Spieler2", "Spieler3", ...],
  "Team B": ["Spieler4", "Spieler5", "Spieler6", ...]
}
```

- Beim Start der Anwendung wird `teams.json` eingelesen und in ein `QStringListModel` geladen.
- Über Buttons können neue Teams angelegt (Eingabefeld für Teamnamen) oder bestehende umbenannt/löschen werden.
- Ein Doppelklick auf einen Team-Eintrag lädt die zugehörigen Spielernamen in die Formation und aktualisiert die Szene per Signal-Slot-Kette (`teamSelected(QString)` → `onTeamSelected(names)`).

Fehlerhafte Einträge (leerer Teamname, doppelte Teams) werden durch Validierungsregeln im Controller abgefangen und dem Benutzer mit einem `QMessageBox` erklärt. Änderungen an `teams.json` werden atomar geschrieben, um Datenkorruption zu vermeiden, indem zuerst in eine temporäre Datei geschrieben und danach umbenannt wird.

## 4. Installation

1. Python 3.8+ installieren  
2. Abhängigkeiten installieren:  
   ```bash
   pip install PyQt6
   ```  
3. Repository klonen und Verzeichnis wechseln:  
   ```bash
   git clone <repo-url>
   cd VolleyballStrategieManager
   ```  
4. Anwendung starten:  
   ```bash
   python main.py
   ```

## 5. Projektstruktur

```
VolleyballStrategieManager/
├── main.py
├── components/
│   ├── player_item.py
│   ├── ball_item.py
│   └── formation_marker_item.py
├── sectors/
│   └── attack_sector.py
├── volleyball_field.py
├── defensive_positions_panel.py
├── team_panel.py
├── interpolation.py
├── utils_common.py
├── utils.py
└── formations.json / teams.json
```

## 6. Bedienung

### 6.1. Spielfeld und Spieler

- **Bewegen**: Linksklick & Ziehen auf einen Spieler  
- **Schlagschatten**: Dynamisch sichtbar, wenn Ball nah am Netz ist

### 6.2. Kontextmenüs

- **Spieler** oder **Zonen** per Rechtsklick für weitere Optionen

### 6.3. Snap-To-Funktion

Ballposition auto-einrasten und Formation laden ab definierter Distanz

## 7. Module im Überblick

- **main.py**: Einstiegspunkt, erstellt Szene, View und Panels  
- **components/player_item.py**: Spieler-Objekte mit Drag & Drop und Zonen  
- **components/ball_item.py**: Ball-Objekt mit Position-Signal und Einraster-Logik  
- **sectors/attack_sector.py**: Visualisiert Angriffssektor um Ball  
- **volleyball_field.py**: Rendering des Spielfelds  
- **defensive_positions_panel.py**: Qt-Widget zur Formationverwaltung  
- **team_panel.py**: Qt-Widget zur Teamverwaltung  
- **interpolation.py**: Logik zur Positionsinterpolation  
- **utils_common.py**, **utils.py**: Hilfsfunktionen  
- **formations.json**, **teams.json**: Persistenz-Daten

## 8. License

Dieses Projekt steht unter der MIT-Lizenz. Weitere Details siehe LICENSE-Datei. 