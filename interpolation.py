import math
from PyQt6.QtCore import QPointF

def point_in_triangle(p, a, b, c):
    """
    Determine if point p is inside triangle abc.
    All points are tuples or lists of (x, y).
    
    Returns True if p is inside triangle abc, False otherwise.
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
    Calculate barycentric coordinates of point p with respect to triangle abc.
    All points are tuples or lists of (x, y).
    
    Returns (alpha, beta, gamma) where p = alpha*a + beta*b + gamma*c
    and alpha + beta + gamma = 1.
    """
    # Calculate triangle area
    denominator = ((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]))
    if abs(denominator) < 1e-10:  # Avoid division by zero
        return (0.33, 0.33, 0.34)  # Return equal weights
    
    # Calculate barycentric coordinates
    alpha = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) / denominator
    beta = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) / denominator
    gamma = 1.0 - alpha - beta
    
    return (alpha, beta, gamma)

def interpolate_position(p, triangles, offsets):
    """
    Interpolate position based on pre-defined triangles and offsets.
    
    Args:
        p: Current ball position as (x, y)
        triangles: List of triangle vertices [(a, b, c), ...] where each vertex is (x, y)
        offsets: List of corresponding player offsets for each triangle vertex
                 [[(offx1, offy1), ...], [(offx2, offy2), ...], ...]
    
    Returns:
        Interpolated offsets as list of (x, y) or None if no interpolation possible
    """
    for i, triangle in enumerate(triangles):
        if point_in_triangle(p, *triangle):
            a, b, c = triangle
            weights = get_barycentric_coordinates(p, a, b, c)
            
            # Get corresponding offsets
            offsets_a = offsets[i][0]
            offsets_b = offsets[i][1]
            offsets_c = offsets[i][2]
            
            # Interpolate offsets for each player
            result = []
            for player_idx in range(len(offsets_a)):
                off_a = offsets_a[player_idx]
                off_b = offsets_b[player_idx]
                off_c = offsets_c[player_idx]
                
                # Weighted average based on barycentric coordinates
                interp_x = weights[0] * off_a[0] + weights[1] * off_b[0] + weights[2] * off_c[0]
                interp_y = weights[0] * off_a[1] + weights[1] * off_b[1] + weights[2] * off_c[1]
                
                result.append((interp_x, interp_y))
            
            return result
            
    return None  # No triangle found containing the point
