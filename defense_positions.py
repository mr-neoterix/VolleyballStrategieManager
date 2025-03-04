from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from PyQt5.QtCore import QPointF
import math
import json
import os

@dataclass
class DefensePosition:
    name: str
    ball_pos: QPointF
    player_positions: Dict[str, QPointF]  # player_label -> position
    
    def to_dict(self):
        """Konvertiert die Position in ein Dictionary für JSON."""
        return {
            'name': self.name,
            'ball_pos': {'x': self.ball_pos.x(), 'y': self.ball_pos.y()},
            'player_positions': {
                label: {'x': pos.x(), 'y': pos.y()}
                for label, pos in self.player_positions.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        """Erstellt eine Position aus einem Dictionary."""
        return cls(
            name=data['name'],
            ball_pos=QPointF(data['ball_pos']['x'], data['ball_pos']['y']),
            player_positions={
                label: QPointF(pos['x'], pos['y'])
                for label, pos in data['player_positions'].items()
            }
        )

class DefensePositionManager:
    def __init__(self):
        self.positions: List[DefensePosition] = []
        self.save_file = "defense_positions.json"
    
    def add_position(self, name: str, ball_pos: QPointF, player_positions: Dict[str, QPointF]):
        self.positions.append(DefensePosition(name, ball_pos, player_positions))
        self.save_positions()
    
    def get_position(self, index: int) -> DefensePosition:
        return self.positions[index]
    
    def get_all_positions(self) -> List[DefensePosition]:
        return self.positions
    
    def save_positions(self):
        """Speichert alle Positionen in eine JSON-Datei."""
        data = [pos.to_dict() for pos in self.positions]
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_positions(self):
        """Lädt alle Positionen aus der JSON-Datei."""
        if not os.path.exists(self.save_file):
            return
            
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            self.positions = [DefensePosition.from_dict(pos_data) for pos_data in data]
        except Exception as e:
            print(f"Fehler beim Laden der Positionen: {e}")
            self.positions = []
    
    def delete_position(self, index: int):
        """Löscht eine Position und speichert die Änderungen."""
        self.positions.pop(index)
        self.save_positions()
    
    def is_inside_triangle(self, point: QPointF) -> bool:
        if len(self.positions) < 3:
            return False
            
        # Berechne die drei Ballpositionen
        p1 = self.positions[0].ball_pos
        p2 = self.positions[1].ball_pos
        p3 = self.positions[2].ball_pos
        
        # Berechne die Fläche des Dreiecks
        def triangle_area(a: QPointF, b: QPointF, c: QPointF) -> float:
            return abs((a.x() * (b.y() - c.y()) + b.x() * (c.y() - a.y()) + c.x() * (a.y() - b.y())) / 2.0)
        
        # Berechne die Fläche des Dreiecks
        area = triangle_area(p1, p2, p3)
        
        # Berechne die Flächen der Teildreiecke mit dem Punkt
        area1 = triangle_area(point, p2, p3)
        area2 = triangle_area(p1, point, p3)
        area3 = triangle_area(p1, p2, point)
        
        # Der Punkt liegt im Dreieck, wenn die Summe der Teildreiecke gleich der Gesamtfläche ist
        return abs(area - (area1 + area2 + area3)) < 1.0
    
    def get_nearest_positions(self, current_ball_pos: QPointF, count: int = 3) -> List[Tuple[DefensePosition, float]]:
        """Gibt die nächstgelegenen Positionen zurück, sortiert nach Abstand."""
        def distance(p1: QPointF, p2: QPointF) -> float:
            return math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
        
        # Berechne die Abstände zu allen Positionen
        distances = []
        for pos in self.positions:
            dist = distance(current_ball_pos, pos.ball_pos)
            distances.append((pos, dist))
        
        # Sortiere nach Abstand und gib die nächstgelegenen zurück
        distances.sort(key=lambda x: x[1])
        return distances[:count]
    
    def interpolate_positions(self, current_ball_pos: QPointF) -> Dict[str, QPointF]:
        if len(self.positions) < 3:
            return {}
            
        # Hole die drei nächstgelegenen Positionen
        nearest_positions = self.get_nearest_positions(current_ball_pos, count=3)
        
        # Berechne die Gewichte basierend auf den Abständen
        total_dist = sum(dist for _, dist in nearest_positions)
        weights = []
        for _, dist in nearest_positions:
            # Je näher, desto höher das Gewicht
            weight = 1.0 / (dist + 0.001)  # Kleine Konstante um Division durch 0 zu vermeiden
            weights.append(weight)
        
        # Normalisiere die Gewichte
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Interpoliere die Spielerpositionen
        interpolated_positions = {}
        for player_label in nearest_positions[0][0].player_positions.keys():
            # Berechne die gewichtete Summe der Positionen
            x = 0
            y = 0
            for (pos, _), weight in zip(nearest_positions, weights):
                player_pos = pos.player_positions[player_label]
                x += weight * player_pos.x()
                y += weight * player_pos.y()
            
            interpolated_positions[player_label] = QPointF(x, y)
        
        return interpolated_positions
    
    def save_positions_to_file(self, file_path: str):
        """Speichert alle Positionen in die angegebene JSON-Datei."""
        data = [pos.to_dict() for pos in self.positions]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2) 