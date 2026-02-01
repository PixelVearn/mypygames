from pathlib import Path

from bat_monster import Bat
from greenslime_monster import GreenSlime
from orc_monster import Orc
from player import Player


def spawn_entities_from_map(
    project_dir: Path,
    rows: list[str],
    tile_size: int,
    display_scale: int,
    map_name: str,
    spawn_tile: tuple[int, int] | None = None,
):
    cleaned_rows = list(rows)

    h = len(cleaned_rows)
    w = len(cleaned_rows[0]) if h > 0 else 0

    def in_bounds(t: tuple[int, int]):
        return 0 <= t[0] < w and 0 <= t[1] < h

    # Option B: spawn everything by position (per map), not by map characters.
    # Symbols used in objects layer:
    # - h: house
    # - t: table
    # - |: door
    # Drops ($/k/p) are spawned dynamically by GamePanel.
    spawn_player: tuple[int, int] | None = None
    bat_tiles: list[tuple[int, int]] = []
    slime_tiles: list[tuple[int, int]] = []
    orc_tiles: list[tuple[int, int]] = []
    objects: dict[tuple[int, int], str] = {}

    if map_name == "map.txt":
        spawn_player = (1, 1)
        objects[(5, 3)] = "h"
        bat_tiles = [(10, 9)]
        slime_tiles = [(18, 14)]
        orc_tiles = [(28, 10)]
    elif map_name == "house.txt":
        objects[(8, 2)] = "t"
        spawn_player = (6, 3)
        objects[(13, 6)] = "|"
        objects[(3, 3)] = "c"
    elif map_name == "cave.txt":
        spawn_player = (1, 1)
        bat_tiles = [(4, 1), (6, 1), (9, 3), (11, 4), (12, 8)]
        orc_tiles = [(7, 7), (10, 6), (14, 9)]
        objects[(8, 5)] = "b"  # blue heart at end of cave
        objects[(4, 5)] = "|"
        objects[(12, 3)] = "c"
    if spawn_player is not None and not in_bounds(spawn_player):
        spawn_player = None

    bat_tiles = [t for t in bat_tiles if in_bounds(t)]
    slime_tiles = [t for t in slime_tiles if in_bounds(t)]
    orc_tiles = [t for t in orc_tiles if in_bounds(t)]
    objects = {t: s for t, s in objects.items() if in_bounds(t)}

    player_assets_dir = project_dir / "player"
    if spawn_tile is not None and in_bounds(spawn_tile):
        player_pos = (spawn_tile[0] * tile_size, spawn_tile[1] * tile_size)
    else:
        if spawn_player is None:
            spawn_player = (3, 3)
        player_pos = (spawn_player[0] * tile_size, spawn_player[1] * tile_size)
    player = Player(player_pos, tile_size, player_assets_dir, scale=display_scale)

    monsters_dir = project_dir / "monster"
    monsters = []
    for tx, ty in bat_tiles:
        monsters.append(Bat((tx * tile_size, ty * tile_size), tile_size, monsters_dir, scale=display_scale))
    for tx, ty in slime_tiles:
        monsters.append(GreenSlime((tx * tile_size, ty * tile_size), tile_size, monsters_dir, scale=display_scale))
    for tx, ty in orc_tiles:
        monsters.append(Orc((tx * tile_size, ty * tile_size), tile_size, monsters_dir, scale=display_scale))

    return cleaned_rows, player, monsters, objects