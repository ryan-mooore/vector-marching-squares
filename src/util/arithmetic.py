"""Helper functions for creating normals.
"""

import math

from classes.coordinates import Coordinates


def create_normal(point1, angle, length):
    point2 = Coordinates(None, None)
    point2.x = point1.x + length * math.sin(math.pi - angle)
    point2.y = point1.y + length * math.cos(math.pi - angle)
    return [point1, point2]


def create_perpendicular_angle(point1, point2):
    return math.atan2(point2.y - point1.y, point2.x - point1.x)
