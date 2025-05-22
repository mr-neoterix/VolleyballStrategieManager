# Wetteranalyse – Dokumentation

**Leon Hübner**  
**Aus der 10/1 vom Wilhelm-Ostwald-Gymnasium**  
**März bis Juni 2022**

---

## Inhaltsverzeichnis

- [Kurzreferat](#kurzreferat) ............................................... 3
- [1. Einleitung](#1-einleitung) .................................... 4
  - [1.1. Themenwahl](#11-themenwahl) ......................... 4
  - [1.2. Zielstellung](#12-zielstellung) ......................... 4
  - [1.3. Motivation](#13-motivation) ............................... 4
- [2. Vorbetrachtung](#2-vorbetrachtung) ................................ 4
  - [2.1. Meteorologie und Wetterbeobachtung](#21-meteorologie-und-wetterbeobachtung) ... 4
  - [2.2. Hardware](#22-hardware) ................................. 5
- [3. Ergebnisse](#3-ergebnisse) ........................................... 7
  - [3.1. Grafische Benutzeroberfläche (GUI)](#31-grafische-benutzeroberflaeche-gui) ... 7
    - [3.1.1. Allgemeines](#311-allgemeines) ......................... 7
    - [3.1.2. Startfenster](#312-startfenster) ...................... 7
    - [3.1.3. Messungs-Fenster](#313-messungs-fenster) ............... 8
    - [3.1.4. Auswertungs-Fenster](#314-auswertungs-fenster) ........ 8
    - [3.1.5. Menüs](#315-menüs) ....................................... 9
  - [3.2. Genutzte Bibliotheken](#32-genutzte-bibliotheken) .............. 9
  - [3.3. Auswertungs-Beispiele](#33-auswertungs-beispiele) .......... 10
- [4. Methoden](#4-methoden) .............................................. 12
  - [4.1. Messungen](#41-messungen) ................................. 12
  - [4.2. Auswertungen](#42-auswertungen) ........................... 13
- [5. Diskussion](#5-diskussion) ........................................... 14
- [6. Abbildungen](#6-abbildungen) ......................................... 16
- [7. Quellen](#7-quellen) ................................................ 18
  - [7.1. Literatur](#71-literatur) ....................................... 18
- [8. Selbstständigkeitserklärung](#8-selbststaendigkeitserklaerung) .......... 18

## Kurzreferat

Im Zeitraum des zweiten Schulhalbjahres wurde im Informatik-Unterricht von Leon Hübner der Klasse 10/1 eine Applikation für die Erfassung und Auswertung von Wetterdaten erstellt. Die Software ist in der Lage, regelmäßige Messungen in festgelegten Intervallen mittels eines geeigneten Messgerätes durchzuführen. Die Messungen beinhalten dabei für das Wetter relevante Größen, darunter Temperatur und Luftfeuchtigkeit. Bei der Auswertung wird ein Diagramm erstellt, das die Messwerte in Abhängigkeit von der Zeit darstellt. Das Programm zeichnet sich durch seine Einfachheit und große Nutzerfreundlichkeit aus. Es findet in vielerlei Bereichen Anwendungsmöglichkeiten, wobei es hauptsächlich für die Langzeitmessung von Wetter konzipiert wurde.

## 1. Einleitung

### 1.1. Themenwahl

Bei dem Projekt handelt es sich um eine Applikation für die naturwissenschaftliche Analyse, genauer gesagt der Analyse von Wetterdaten. Damit ist es in die Meteorologie, die Wissenschaft über die Prozesse der Atmosphäre, einzuordnen.

### 1.2. Zielstellung

Das Ziel war ein Programm, das in der Lage ist, physikalische Größen aufzunehmen und anschließend auszuwerten. Zu diesen Größen gehören für das Wetter relevante Eigenschaften, insbesondere Temperatur, Luftfeuchtigkeit und Luftdruck. Die Auswertung besteht aus einem Diagramm sowie statistischen Größen.

### 1.3. Motivation

Die meisten Menschen nutzen täglich einen Wetterbericht, den sie zum Beispiel im Radio hören. Er ist nützlich, um sich wettergerecht zu kleiden, aber auch für die Planung des Tagesablaufs und Aktivitäten, die im Freien stattfinden. Wetterberichte sind Prognosen für zukünftige Entwicklungen auf Grundlage von Messdaten. Möglichst solide Wetter-Daten zu erfassen und auszuwerten, ist daher ein zentraler Bestandteil der Wetterberichte. Aber auch wissenschaftlicher Experimente oder die Überwachung von Systemen wie Aquarien benötigen die Erfassung und Auswertung von physikalischen Größen. Eine Software, die diese Aufgabe erfüllen kann, hat daher viele Einsatzbereiche, für die sich eine Entwicklung lohnt.

## 2. Vorbetrachtung

### 2.1. Meteorologie und Wetterbeobachtung

Die Meteorologie ist die Wissenschaft der physikalischen und chemischen Vorgänge der Atmosphäre. Das Projekt beschränkt sich auf die Aufnahme und Auswertung von physikalischen Größen, weshalb es in das Teilgebiet Wetterbeobachtung einzuordnen ist. Im Gegensatz zu anderen Teilgebieten sucht die Wetterbeobachtung keine wissenschaftlichen Erklärungen für die Messwerte. Sie ist damit aber auch die Grundlage für alle anderen Gebiete.

Bereits seit Jahrtausenden beschäftigen sich die Menschen mit der Beobachtung des Wetters, die vor allem für die Aussaat und Ernte wichtig war. Es entstanden die sogenannten Bauernregeln. 1781 begann ein namhaftes Instrument regelmäßig Messwerte aufzunehmen. Im 19. Jahrhundert wurden erste Wetterballons für die Messung in großen Höhen entwickelt. Heute gibt es unzählige Messstationen auf dem Land, in Bojen auf dem Meer und in der Luft als Wetterballons. Sie werden von den Wetterdiensten betrieben und senden diesen regelmäßig auf digitalem Wege ihre Daten.

Man kann die Wetterbeobachtung in zwei Bereiche unterteilen. Der erste umfasst Eigenschaften, die man nicht direkt messen kann, sondern wortwörtlich beobachten muss. Dazu zählen zum Beispiel die Art der Wolken, deren Menge, evtl. Nebel oder auch die Verfärbung beim Sonnenaufgang und -untergang. Der zweite Bereich umfasst direkt messbare Größen, unter anderem Temperatur, Luftfeuchtigkeit und -druck, Helligkeit, Niederschlagsmenge und einige mehr. Für das Projekt wurden wenige Größen gewählt, die mit geeigneten Sensoren leicht zu messen sind.

### 2.2. Hardware

Die Hardware setzt sich aus zwei verschiedenen Komponenten zusammen. Sensoren (DHT22 und BMP280) dienen der direkten Messung der verschiedenen Größen. Für die Verarbeitung (Umwandlung in Daten) und die Speicherung wird ein Minicomputer (Raspberry Pi) verwendet.

Als Minicomputer wurde der Raspberry Pi 2 Model B genutzt. Dieser besitzt eine sogenannte GPIO-Leiste mit über 40 Anschlüssen, welche als digitale Ein- bzw. Ausgänge für Sensoren dienten. Weil nur digitale Signale aufgenommen werden können, müssen Sensoren die analogen Messwerte durch einen integrierten AD-Wandler (Analog-Digital-Wandler) in Nullen und Einsen (= digitales Signal) übersetzen. Diese Signale werden schließlich durch den Raspberry Pi 2 in Messwerte umgewandelt. Dazu wurden Bibliotheken der jeweiligen Hersteller genutzt.

Für die Aufnahme der Messwerte standen zwei verschiedene Sensoren zur Verfügung:

1. **DHT22 (AM2302)**: Misst Temperatur (-40 bis 80 °C) mit einer Genauigkeit von ±0,5 °C und Luftfeuchtigkeit (0–100 %) mit einer Genauigkeit von 2–5 %. Der Sensor verfügt über vier Anschlüsse, von denen drei genutzt werden (3,3 V, Masse, Daten). Angeschlossen wird er gemäß Schaltplan an einen GPIO-Pin mit Pull-Up-Widerstand.
2. **BMP280 (Bosch)**: Misst Temperatur (-40 bis 85 °C) mit ±0,5 °C und Luftdruck (300 bis 1100 hPa) mit ±0,12 hPa. Er hat sechs Anschlüsse, wovon vier genutzt werden (3,3 V, Masse, SCL, SDA). Diese werden an zwei beliebige GPIO-Pins (SCL an Pin X, SDA an Pin Y) des Raspberry Pi angeschlossen.

## 3. Ergebnisse

### 3.1. Grafische Benutzeroberfläche (GUI)

#### 3.1.1. Allgemeines

Das Projekt verfügt über eine GUI, die aus drei bedeutsamen Fenstern besteht. Allen Elementen und Widget-Namen liegt eine feste Benennungsvorschrift zugrunde, die zur Übersichtlichkeit des Codes beiträgt. Je nach Klasse der Objekte beginnt der Name mit unterschiedlichen Großbuchstaben oder Abkürzungen:

- **B_**: Button
- **L_**: Label (statisch)
- **A_**: Label (dynamisch)
- **E_**: Eingabezeile
- **Check_**: Checkbox
- **Combo_**: Combobox

#### 3.1.2. Startfenster

Das Startfenster begrüßt den Nutzer mit einer Abbildung und zwei Buttons: „Messung starten“ und „Messung auswerten“. Je nach Auswahl öffnet sich das entsprechende Fenster für Messung oder Auswertung.

#### 3.1.3. Messungs-Fenster

Das Messungs-Fenster ermöglicht das Starten einer Messung:

1. Auswahl des Speicherorts über einen Dateiexplorer.
2. Eingabe des Messungsnamens.
3. Auswahl des Sensors per Combobox und ggf. der zugehörigen GPIO-Pins.
4. Eingabe der Messparameter (Temperatur, Luftfeuchtigkeit, Luftdruck): Zwei Felder sind nötig, das dritte wird automatisch berechnet.
5. Start/Abbrechen der Messung per Button. Ausgabe erfolgt in einer Text-Area.

#### 3.1.4. Auswertungs-Fenster

Das Auswertungs-Fenster bietet:

- Wahl des Messpfads.
- Auswahl der auszuwertenden Größen per Checkbox.
- Optionaler Zeitfenster-Filter mit aktivierbaren Eingabefeldern.
- Darstellung von Minima, Maxima und Durchschnitt in einer Tabelle.
- Anzeige des Diagramms (Matplotlib) mit Einstellungsoptionen.
- Button zum Öffnen des Diagramms in einem neuen Fenster.

#### 3.1.5. Menüs

Beide Fenster (Messung & Auswertung) besitzen ein **Datei**-Menü mit den Optionen **Schließen** (```self.close()```) und **Beenden** (```sys.exit()```). Im Messungs-Fenü gibt es zusätzlich ein **Fenster**-Menü zum Wechsel zwischen den Fenstern und ein **Hilfe**-Menü mit Kurzanleitungen und Verweisen auf Tutorial-Websites.

### 3.2. Genutzte Bibliotheken

Es wurden u. a. folgende Bibliotheken verwendet:

- **Matplotlib**: Erzeugung und Einbettung von Diagrammen in die GUI.
- **PySide6**: Erstellung der Benutzeroberfläche.
- **Adafruit_DHT** bzw. **CircuitPython-BMP280**: Einlesen der Sensordaten auf dem Raspberry Pi.

```python
import matplotlib.pyplot as plt
plt.plot(xWerte, yWerte)
self.figur = plt.figure()
self.canvas = FigureCanvas(self.figur)
self.ui.L_diagramm.addWidget(self.canvas)
```

### 3.3. Auswertungs-Beispiele

Beispiel 1: Temperatur und Luftfeuchtigkeit über ca. 13 Stunden (Ziel: 38,3 °C und 60 % Luftfeuchte). Schwankungen sind im Diagramm ersichtlich.

Beispiel 2: Kurzzeitmessung (~10 Minuten): Verlauf von 20 °C auf 38 °C. Zusammenhang Temperatur ↔ Luftfeuchte gut erkennbar.

## 4. Methoden

### 4.1. Messungen

Eine Messung gliedert sich in 3 Schritte: **Messen**, **Speichern**, **Warten**:

- _Messen_: Auslesen der Sensorbibliotheken und Runden der Werte mit `round(zahl, n)`.
- _Speichern_: Öffnen und Anhängen der Werte in Dateien (`datei.write()`, `datei.close()`).
- _Warten_: Einsatz eines `QTimer` statt `sleep()`, um die GUI reaktionsfähig zu halten.

### 4.2. Auswertungen

- Einlesen der Messdaten (`datei.read()`, `split()`).
- Umwandlung in `float` und `datetime`.
- Berechnung von `min()`, `max()` und Durchschnitt (eigene Funktion).
- Filterung nach Zeitfenster durch Indexsuche im Zeitarray.

## 5. Diskussion

Es wurden alle Soll- und Kann-Kriterien erfüllt: Messungen, Speicherung, Auswertung (Min, Max, Durchschnitt), Diagramm, GUI-Design, Zeitfilter, Kurzanleitungen und Export. Als Erweiterung könnten Messfehlererkennung oder Heizelement-Steuerung implementiert werden. Insgesamt übertraf das Projekt die Erwartungen.

## 6. Abbildungen

**Startfenster:**

*Screenshot einfügen*

**Messungsfenster:**

*Screenshot einfügen*

## 7. Quellen

### 7.1. Literatur

- Literaturangaben hier einfügen...

## 8. Selbstständigkeitserklärung

Selbstständigkeitserklärung hier einfügen... 