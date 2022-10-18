"""Primitive renderer of isoline-paths files.
"""

import math

import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d

from classes.coordinates import Coordinates
from util.arithmetic import create_normal, create_perpendicular_angle
from util.read_write import import_file

COLOR = "#BA5E1A"

DEBUG = False
DEBUG_MAX = 32

SMOOTHNESS = 1
SMOOTHNESS_CROP = 3

data = import_file()
width = data["dimensions"]["width"]
height = data["dimensions"]["height"]


def smoothen(x, y, smoothness, is_closed=True):
    if smoothness:
        if is_closed:
            x_start, x_end = x[0:SMOOTHNESS_CROP], x[-SMOOTHNESS_CROP:]
            y_start, y_end = y[0:SMOOTHNESS_CROP], y[-SMOOTHNESS_CROP:]
            x = x_end + x + x_start
            y = y_end + y + y_start

        x = gaussian_filter1d(x, smoothness)
        y = gaussian_filter1d(y, smoothness)

        if is_closed:
            x = x[SMOOTHNESS_CROP : -SMOOTHNESS_CROP + 1]
            y = y[SMOOTHNESS_CROP : -SMOOTHNESS_CROP + 1]
    return Coordinates.from_list(x, y)


def debug_plot(isoline, open=True):
    x = isoline["path"]["x"]
    y = isoline["path"]["y"]

    plt.plot(x[0], y[0], "go")  # plot green line at start of isoline
    if not open:
        # add red point 1 point away from end so points are not on top
        # of each other
        plt.plot(x[len(x) - 2], y[len(y) - 2], "ro")
    else:
        plt.plot(
            x[len(x) - 1], y[len(y) - 1], "ro"
        )  # add red point at end for open isoline

    # left by default
    vertices = Coordinates.from_list(x, y)
    for point1, point2 in zip(vertices, vertices[1:]):
        point_middle = Coordinates((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)
        normal_ang = create_perpendicular_angle(point1, point2)
        if open:
            if isoline["downslope"] == "right":
                normal_ang += math.pi  # add 180 if downslope is on other side
        elif (
            isoline["type"] == "hill"
        ):  # all closed isolines are anti-clockwise, so hills have downslope on right
            normal_ang += math.pi

        normal = create_normal(point_middle, normal_ang, 0.2)
        plt.plot(*Coordinates.to_list(normal), color="#000")  # plot tags

    plt.plot(x, y, linewidth=1, color="#000")  # plot isoline
    plt.text(x[0], y[0], value, color="g")


def plot(isoline, open=True):
    for x, y in zip(isoline["path"]["x"], isoline["path"]["y"]):
        x += 0.5
        y += 0.5
    plt.plot(
        *Coordinates.to_list(
            smoothen(
                isoline["path"]["x"],
                isoline["path"]["y"],
                SMOOTHNESS,
                is_closed=not open,
            )
        ),
        color=COLOR,
        linewidth=3,
    )


plt.close()

if DEBUG:
    plt.figure(f"Debugging")
else:
    plt.figure(f"Isoline plot")

axes = plt.gca()
graph = plt.gcf()

axes.invert_yaxis()
axes.set_aspect(1)

if DEBUG:
    max_h = min(height, DEBUG_MAX)
    max_w = min(width, DEBUG_MAX)

    graph.set_size_inches(8, 8)
    plt.ylim(max_h, 0)
    plt.xlim(0, max_w)
    plt.xticks(range(0, max_w + 1))
    plt.yticks(range(0, max_h + 1))

    plt.grid(color="#000", linestyle="-", linewidth=1, which="both")

    for value, isoline in enumerate(data["isolines"]["open"]):
        debug_plot(isoline, open=True)
    for value, isoline in enumerate(data["isolines"]["closed"], start=value + 1):
        debug_plot(isoline, open=False)
else:
    plt.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    if graph.canvas.toolbar:
        try:
            graph.canvas.toolbar.pack_forget()
        except AttributeError:
            pass
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    for isoline in data["isolines"]["open"]:
        plot(isoline, open=True)
    for isoline in data["isolines"]["closed"]:
        plot(isoline, open=False)

plt.show()
