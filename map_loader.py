from __future__ import annotations

from pathlib import Path


def load_map_file(path: Path, numeric_legend: dict[int, str] | None = None):
    """Load a tile map from a text file.

    Supports:
    - Character maps: each line is a row of characters (e.g. .#~)
    - Numeric maps: space-separated integers per row (e.g. 0 0 1 1)

    Returns: list[str] where each string is a row of tile characters.
    """

    if numeric_legend is None:
        numeric_legend = {
            0: ".",  # grass
            1: "#",  # wall
            2: "~",  # water
            3: "V",  # void
            4: "T",  # tree
            5: "1",  # water corner 1
            6: "2",  # water center up
            7: "3",  # water corner 2
            8: "4",  # water center right
            9: "5",  # water corner 3
            10: "6",  # water center down
            11: "7",  # water corner 4
            12: "8",  # water center left
            13: "9",  # road
            14: "A",  # road corner 1
            15: "B",  # road center up
            16: "C",  # road corner 2
            17: "D",  # road center right
            18: "E",  # road corner 3
            19: "F",  # road center down
            20: "G",  # road corner 4
            21: "H",  # road center left
            22: "I",  # water external corner 1
            23: "J",  # water external corner 2
            24: "K",  # water external corner 3
            25: "L",  # water external corner 4
            26: "M",  # dirt ground
            27: "N",  # wood floor
            28: "u",  # stairs up
            29: "d",  # stairs down
           
        }

    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[str] = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Numeric map if it contains spaces and starts with a digit or '-'.
        if (" " in line or "\t" in line) and (line[0].isdigit() or line[0] == "-"):
            tokens = line.replace("\t", " ").split()
            chars = []
            for t in tokens:
                try:
                    n = int(t)
                except ValueError:
                    n = 0
                chars.append(numeric_legend.get(n, "."))
            rows.append("".join(chars))
        else:
            # Character map: remove spaces so you can write '. . # #' too.
            compact = "".join(ch for ch in line if ch != " ")

            # Allow digit maps without spaces (e.g. 001122) in the same file.
            if compact and all(ch.isdigit() for ch in compact):
                chars = []
                for ch in compact:
                    n = int(ch)
                    chars.append(numeric_legend.get(n, "."))
                rows.append("".join(chars))
            else:
                rows.append(compact)

    if not rows:
        return rows

    # Make it a clean rectangle (pad short rows with grass '.', trim long rows).
    w = max(len(r) for r in rows)
    rect = []
    for r in rows:
        if len(r) < w:
            rect.append(r + ("." * (w - len(r))))
        else:
            rect.append(r[:w])

    return rect
