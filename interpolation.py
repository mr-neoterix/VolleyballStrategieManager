import math  # Importiert das math-Modul für mathematische Operationen.
from PyQt6.QtCore import QPointF  # Importiert QPointF von PyQt6 für die Arbeit mit 2D-Punkten mit Fließkommazahlen.

def point_in_triangle(p, a, b, c):  # Definiert eine Funktion, um zu prüfen, ob ein Punkt in einem Dreieck liegt.
    """
    Prüft, ob ein Punkt p innerhalb des Dreiecks abc liegt.
    Alle Punkte sind Tupel oder Listen mit (x, y)-Koordinaten.
    
    Gibt True zurück, wenn p im Dreieck liegt, sonst False.
    """
    def sign(p1, p2, p3):  # Definiert eine Hilfsfunktion zur Bestimmung der Orientierung von drei Punkten.
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])  # Berechnet das Vorzeichen basierend auf dem Kreuzprodukt.
    
    d1 = sign(p, a, b)  # Berechnet die Orientierung des Punktes p relativ zur Seite ab.
    d2 = sign(p, b, c)  # Berechnet die Orientierung des Punktes p relativ zur Seite bc.
    d3 = sign(p, c, a)  # Berechnet die Orientierung des Punktes p relativ zur Seite ca.
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)  # Prüft, ob eine der Orientierungen negativ ist.
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)  # Prüft, ob eine der Orientierungen positiv ist.
    
    return not (has_neg and has_pos)  # Gibt True zurück, wenn alle Orientierungen dasselbe Vorzeichen haben (oder null sind), andernfalls False.

def get_barycentric_coordinates(p, a, b, c):  # Definiert eine Funktion zur Berechnung baryzentrischer Koordinaten.
    """
    Berechnet die baryzentrischen Koordinaten des Punkts p bezüglich des Dreiecks abc.
    Alle Punkte sind Tupel oder Listen mit (x, y)-Koordinaten.
    
    Gibt (alpha, beta, gamma) zurück, wobei p = alpha*a + beta*b + gamma*c
    und alpha + beta + gamma = 1.
    """
    # Berechnet die Dreiecksfläche (doppelt, vorzeichenbehaftet)
    denominator = ((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]))  # Berechnet den Nenner für die baryzentrischen Koordinaten (proportional zur Dreiecksfläche).
    if abs(denominator) < 1e-10:  # Vermeidet Division durch Null für kollineare Punkte.
        return (0.33, 0.33, 0.34)  # Gibt gleichmäßige Gewichte zurück, falls das Dreieck entartet ist.
    
    # Berechnet baryzentrische Koordinaten
    alpha = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) / denominator  # Berechnet die Koordinate alpha.
    beta = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) / denominator  # Berechnet die Koordinate beta.
    gamma = 1.0 - alpha - beta  # Berechnet die Koordinate gamma, da die Summe 1 sein muss.
    
    return (alpha, beta, gamma)  # Gibt die baryzentrischen Koordinaten als Tupel zurück.

def interpolate_position(p, triangles, offsets):  # Definiert eine Funktion zur Interpolation von Positionen basierend auf Dreiecken.
    """
    Interpoliert Positionen basierend auf vordefinierten Dreiecken und Offsets.
    
    Parameter:
        p: Aktuelle Ballposition als (x, y)  # Die Position, für die interpoliert werden soll.
        triangles: Liste von Dreiecksecken [(a, b, c), ...] wobei jede Ecke (x, y) ist  # Eine Liste von Dreiecken, die den Raum abdecken.
        offsets: Liste entsprechender Spieler-Offsets für jede Dreiecksecke  # Offsets, die den Eckpunkten der Dreiecke zugeordnet sind.
                 [[(offx1, offy1), ...], [(offx2, offy2), ...], ...]
    
    Gibt zurück:
        Interpolierte Offsets als Liste von (x, y) oder None, wenn keine Interpolation möglich ist  # Die interpolierten Offsets oder None.
    """
    for i, triangle in enumerate(triangles):  # Iteriert über alle definierten Dreiecke mit ihrem Index.
        if point_in_triangle(p, *triangle):  # Prüft, ob der Punkt p im aktuellen Dreieck liegt.
            a, b, c = triangle  # Entpackt die Eckpunkte des Dreiecks.
            weights = get_barycentric_coordinates(p, a, b, c)  # Berechnet die baryzentrischen Koordinaten von p im Dreieck.
            
            # Holt die entsprechenden Offsets
            offsets_a = offsets[i][0]  # Holt die Offsets, die dem ersten Eckpunkt (a) des Dreiecks zugeordnet sind.
            offsets_b = offsets[i][1]  # Holt die Offsets, die dem zweiten Eckpunkt (b) des Dreiecks zugeordnet sind.
            offsets_c = offsets[i][2]  # Holt die Offsets, die dem dritten Eckpunkt (c) des Dreiecks zugeordnet sind.
            
            # Interpoliert Offsets für jeden Spieler
            result = []  # Initialisiert eine leere Liste für die resultierenden interpolierten Offsets.
            for player_idx in range(len(offsets_a)):  # Iteriert über die Anzahl der Spieler (basierend auf der Länge der Offset-Liste für einen Eckpunkt).
                off_a = offsets_a[player_idx]  # Holt den Offset des aktuellen Spielers für Eckpunkt a.
                off_b = offsets_b[player_idx]  # Holt den Offset des aktuellen Spielers für Eckpunkt b.
                off_c = offsets_c[player_idx]  # Holt den Offset des aktuellen Spielers für Eckpunkt c.
                
                # Gewichteter Durchschnitt basierend auf baryzentrischen Koordinaten
                interp_x = weights[0] * off_a[0] + weights[1] * off_b[0] + weights[2] * off_c[0]  # Interpoliert die x-Koordinate des Offsets.
                interp_y = weights[0] * off_a[1] + weights[1] * off_b[1] + weights[2] * off_c[1]  # Interpoliert die y-Koordinate des Offsets.
                
                result.append((interp_x, interp_y))  # Fügt den interpolierten Offset zur Ergebnisliste hinzu.
            
            return result  # Gibt die Liste der interpolierten Offsets zurück.
            
    return None  # Kein Dreieck gefunden, das den Punkt enthält. Gibt None zurück, wenn p in keinem der Dreiecke liegt.
