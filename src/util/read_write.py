"""Helper functions for IO.
"""


from classes.coordinates import Coordinates
from json import dumps, loads


def export(height, width, open_isolines, closed_isolines):
    json = {
        "dimensions": {"width": width, "height": height},
        "isolines": {"open": [], "closed": []},
    }
    for isoline in open_isolines:
        json["isolines"]["open"].append(
            {
                "path": {
                    "x": Coordinates.to_list(isoline.vertices)[0],
                    "y": Coordinates.to_list(isoline.vertices)[1],
                },
                "elevation": isoline.elevation,
                "downslope": isoline.downslope,
            }
        )
    for isoline in closed_isolines:
        json["isolines"]["closed"].append(
            {
                "path": {
                    "x": Coordinates.to_list(isoline.vertices)[0],
                    "y": Coordinates.to_list(isoline.vertices)[1],
                },
                "elevation": isoline.elevation,
                "type": isoline.__class__.__name__.lower(),
            }
        )

    open("isoline-paths.json", "w").write(dumps(json))


def import_file():
    return loads(open("isoline-paths.json", "r").read())
