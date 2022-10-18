"""Vector marching squares implementation.
Tracing algorithm is detailed in tracing.py"""

from sys import argv

import numpy as np
from PIL import Image

from classes.cellmap import CellMap, Edge
from classes.isolines import ClosedIsoline
from tracing import start_traces, trace_from_here
from util.read_write import export

open_isolines = []
closed_isolines = []
blockmap = np.array(Image.open(argv[1])).astype(int)
cellmap = CellMap(blockmap)


# kick off tracing from all four edges of the bounding area.
# this will find all the open-ended isolines within the
# bounded areas (open isolines will always touch the edge)
for cell in cellmap.cellmap[0]:
    open_isolines.extend(
        start_traces(cell, Edge.name.TOP.value, cellmap.height, cellmap.width)
    )
for row in cellmap.cellmap:
    open_isolines.extend(
        start_traces(
            row[len(row) - 1], Edge.name.RIGHT.value, cellmap.height, cellmap.width
        )
    )
for cell in cellmap.cellmap[len(cellmap.cellmap) - 1]:
    open_isolines.extend(
        start_traces(cell, Edge.name.BOTTOM.value, cellmap.height, cellmap.width)
    )
for row in cellmap.cellmap:
    open_isolines.extend(
        start_traces(row[0], Edge.name.LEFT.value, cellmap.height, cellmap.width)
    )

# iterate through each cell to find remaining isolines to be traced
# this will find the remaining, closed ('O') isolines.
for row in cellmap.cellmap:
    for cell in row:
        for edge in cell.edges:
            if edge.direction == 1:
                for elevation in range(edge.corner1, edge.corner2):
                    if not edge.isolines[elevation]:
                        isoline = trace_from_here(
                            cell,
                            edge,
                            elevation,
                            cellmap.height,
                            cellmap.width,
                            ClosedIsoline,
                        )
                        if isoline:
                            closed_isolines.append(isoline)
            if edge.direction == -1:
                for elevation in range(edge.corner1 - 1, edge.corner2 - 1, -1):
                    if not edge.isolines[elevation]:
                        isoline = trace_from_here(
                            cell,
                            edge,
                            elevation,
                            cellmap.height,
                            cellmap.width,
                            ClosedIsoline,
                        )
                        if isoline:
                            closed_isolines.append(isoline)

export(cellmap.height, cellmap.width, open_isolines, closed_isolines)
