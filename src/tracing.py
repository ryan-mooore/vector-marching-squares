"""Vector marching squares tracing algorithm.
"""

from classes.coordinates import Coordinates
from classes.isolines import ClosedIsoline, Isoline, OpenIsoline

INTERVAL = 1
PHASE = 0


def traverse(cell, edge):
    cells = [*edge.cells]
    cells.remove(cell)
    return cells[0]


def get_point_pos(height, edge):
    point = (height - edge.min_corner() + 1) / (edge.difference + 1)
    if edge.direction == -1:
        point = 1 - point
    return point


def height_within_difference(height, edge):
    return (
        edge.min_corner() <= height < edge.max_corner()
    )  # an isoline starts at this edge at this height


def find_direction(first, second, height, width):
    if len(first.cells) == 1:
        if first.axis == "x" and first.cells[0].coords.y == 0:
            return "left" if first.direction == -1 else "right"
        elif first.axis == "x" and first.cells[0].coords.y == height - 1:
            return "left" if first.direction == 1 else "right"
        elif first.axis == "y" and first.cells[0].coords.x == 0:
            return "left" if first.direction == 1 else "right"
        elif first.axis == "y" and first.cells[0].coords.x == width - 1:
            return "left" if first.direction == -1 else "right"
    else:
        if first.axis == "x":
            if first.cells[0] in second.cells:  # moving up
                return "left" if first.direction == 1 else "right"
            else:
                return "left" if first.direction == -1 else "right"
        if first.axis == "y":
            if first.cells[0] in second.cells:  # moving left
                return "left" if first.direction == -1 else "right"
            else:
                return "left" if first.direction == 1 else "right"


def add_point(isoline, elevation, edge, cell_coords, height, width):
    if edge.axis == "x":
        vertice = Coordinates(
            cell_coords.x + get_point_pos(elevation, edge),
            edge.axis_pos,  # on an x axis edge so y is a known and whole number
        )
    else:  # edge.axis == "y":
        vertice = Coordinates(
            edge.axis_pos,  # on an y axis edge so x is a known and whole number
            cell_coords.y + get_point_pos(elevation, edge),
        )

    if hasattr(isoline, "edge_for_finding_direction"):
        isoline.downslope = find_direction(
            isoline.edge_for_finding_direction, edge, height, width
        )
        del isoline.edge_for_finding_direction

    isoline.vertices.append(vertice)


def trace_from_here(cell, edge, elevation, height, width, isoline_type) -> Isoline:
    if height_within_difference(elevation, edge):

        isoline = isoline_type(elevation)

        edge.isolines[elevation]["isoline"] = isoline
        edge.isolines[elevation]["start"] = True
        add_point(isoline, elevation, edge, cell.coords, height, width)
        isoline.edge_for_finding_direction = edge

        # trace
        while True:
            edges = [*cell.edges]
            edges.remove(edge)
            edges.sort(
                key=lambda e: e.axis == edge.axis
            )  # sort by adjacent first, then opposite (to avoid crossover)
            for edge in edges:
                if height_within_difference(elevation, edge):
                    if edge.isolines[
                        elevation
                    ]:  # if an isoline at the same height exists
                        if (
                            isinstance(isoline, ClosedIsoline)
                            and edge.isolines[elevation]["isoline"] == isoline
                        ):  # we only need to consider this edge if the isoline needs to be closed and is the same one we are tracing
                            if "start" in edge.isolines[elevation]:
                                add_point(
                                    isoline, elevation, edge, cell.coords, height, width
                                )
                                return (isoline := isoline.get_type())
                                # if no then we have reached the same isoline but haven't looped back to the start yet. Try another edge
                        continue  # if the isoline does not need to be closed we don't care. we can't go to this edge. Try another edge
                    else:
                        pass
                        # no existing isoline, easy trace to this edge

                    edge.isolines[elevation][
                        "isoline"
                    ] = isoline  # mark the edge as visited
                    add_point(
                        isoline, elevation, edge, cell.coords, height, width
                    )  # and add the coordinates to the isoline

                    if (
                        len(edge.cells) == 1
                    ):  # if the boundary has been hit the isoline is complete
                        return isoline
                    else:
                        cell = traverse(cell, edge)  # otherwise trace again!
                        break  # go to next cell
            else:
                # this should never occur. if it does it means that there were no edges to trace to and the isoline has to end prematurely
                break  # do not draw the isoline


def start_traces(cell, edgename, height, width) -> list[Isoline]:
    isolines = []
    edge = cell.edges[edgename]
    for elevation in range(
        edge.min_corner(), edge.max_corner() + 1
    ):  # start a trace for every height in the cell
        if elevation % (INTERVAL + PHASE) == 0:  # check isoline is at correct interval
            if not edge.isolines[
                elevation
            ]:  # check that an isoline hasn't already been traced to here
                isoline = trace_from_here(
                    cell, cell.edges[edgename], elevation, height, width, OpenIsoline
                )  #  and start the trace
                if isoline:  # check that the isoline is actually a line
                    isolines.append(isoline)
    return isolines
