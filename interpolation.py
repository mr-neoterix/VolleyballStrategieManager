import math
from PyQt6.QtCore import QPointF

def point_in_triangle(p, a, b, c):
    """
    Prüft, ob ein Punkt p innerhalb des Dreiecks abc liegt.
    Alle Punkte sind Tupel oder Listen mit (x, y)-Koordinaten.
    
    Gibt True zurück, wenn p im Dreieck liegt, sonst False.
    """
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    d1 = sign(p, a, b)
    d2 = sign(p, b, c)
    d3 = sign(p, c, a)
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    
    return not (has_neg and has_pos)

def get_barycentric_coordinates(p, a, b, c):
    """
    Berechnet die baryzentrischen Koordinaten des Punkts p bezüglich des Dreiecks abc.
    Alle Punkte sind Tupel oder Listen mit (x, y)-Koordinaten.
    
    Gibt (alpha, beta, gamma) zurück, wobei p = alpha*a + beta*b + gamma*c
    und alpha + beta + gamma = 1.
    """
    # Berechnet die Dreiecksfläche
    denominator = ((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]))
    if abs(denominator) < 1e-10:  # Vermeidet Division durch Null
        return (0.33, 0.33, 0.34)  # Gibt gleichmäßige Gewichte zurück
    
    # Berechnet baryzentrische Koordinaten
    alpha = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) / denominator
    beta = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) / denominator
    gamma = 1.0 - alpha - beta
    
    return (alpha, beta, gamma)

def interpolate_position(p, triangles, offsets):
    """
    Interpoliert Positionen basierend auf vordefinierten Dreiecken und Offsets.
    
    Parameter:
        p: Aktuelle Ballposition als (x, y)
        triangles: Liste von Dreiecksecken [(a, b, c), ...] wobei jede Ecke (x, y) ist
        offsets: Liste entsprechender Spieler-Offsets für jede Dreiecksecke
                 [[(offx1, offy1), ...], [(offx2, offy2), ...], ...]
    
    Gibt zurück:
        Interpolierte Offsets als Liste von (x, y) oder None, wenn keine Interpolation möglich ist
    """
    for i, triangle in enumerate(triangles):
        if point_in_triangle(p, *triangle):
            a, b, c = triangle
            weights = get_barycentric_coordinates(p, a, b, c)
            
            # Holt die entsprechenden Offsets
            offsets_a = offsets[i][0]
            offsets_b = offsets[i][1]
            offsets_c = offsets[i][2]
            
            # Interpoliert Offsets für jeden Spieler
            result = []
            for player_idx in range(len(offsets_a)):
                off_a = offsets_a[player_idx]
                off_b = offsets_b[player_idx]
                off_c = offsets_c[player_idx]
                
                # Gewichteter Durchschnitt basierend auf baryzentrischen Koordinaten
                interp_x = weights[0] * off_a[0] + weights[1] * off_b[0] + weights[2] * off_c[0]
                interp_y = weights[0] * off_a[1] + weights[1] * off_b[1] + weights[2] * off_c[1]
                
                result.append((interp_x, interp_y))
            
            return result
            
    return None  # Kein Dreieck gefunden, das den Punkt enthält
