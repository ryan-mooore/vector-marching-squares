"""Isoline class definitions.
"""

import math

from scipy.spatial import ConvexHull
from util.arithmetic import create_perpendicular_angle


class Isoline:
    def __init__(self, elevation) -> None:
        self.vertices = []
        self.downslope = None
        self.elevation = elevation

    def __repr__(self) -> str:
        return "---".join([repr(cell[1]) for cell in self.isoline])


class ClosedIsoline(Isoline):
    def __init__(self, elevation) -> None:
        super().__init__(elevation)

    def get_type(self):
        hull = ConvexHull([(c.x, c.y) for c in self.vertices])
        angles = []
        for index, vertice in enumerate(self.vertices):
            if index in hull.vertices:
                angles.append(vertice)
            if len(angles) == 3:
                break
        a, b, c = angles

        angle = create_perpendicular_angle(b, c) - create_perpendicular_angle(a, b)
        if angle < math.pi:
            # orientation is anti-clockwise
            if self.downslope == "right":
                return Hill(self)
            else:
                return Depression(self)
        else:  # angle > math.pi:
            # orientation is clockwise

            self.vertices.reverse()  # ensure that vertices will always be anticlockwise

            if self.downslope == "right":
                return Depression(self)
            else:
                return Hill(self)


class OpenIsoline(Isoline):
    def __init__(self, elevation) -> None:
        super().__init__(elevation)


class Depression(ClosedIsoline):
    def __init__(self, isoline):
        super().__init__(elevation=isoline.elevation)
        self.vertices = isoline.vertices
        self.extremum = None
        self.contains = []


class Hill(ClosedIsoline):
    def __init__(self, isoline):
        super().__init__(elevation=isoline.elevation)
        self.vertices = isoline.vertices
        self.extremum = None
        self.contains = []
