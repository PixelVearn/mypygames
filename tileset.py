from pathlib import Path
from tarfile import XHDTYPE

import pygame

from assets import load_image


class TileSet:
    def __init__(self, tiles_dir: Path, display_scale: int):
        self.display_scale = display_scale

        self.tiles = []
        self.tile_paths = []
        for i in range(38):
            name = f"{i:03d}.png"
            p = tiles_dir / name
            self.tile_paths.append(p)
            img = load_image(p)
            self.tiles.append(
                pygame.transform.scale(
                    img,
                    (img.get_width() * display_scale, img.get_height() * display_scale),
                )
            )

        # New tileset uses numbered files (000.png ... 037.png).
        # These defaults are picked to look reasonable with the provided set.
        void = load_image(tiles_dir / "000.png")
        grass = load_image(tiles_dir / "001.png")
        water = load_image(tiles_dir / "018.png")
        wall = load_image(tiles_dir / "032.png")
        tree = load_image(tiles_dir / "016.png")
        water_corner1 = load_image(tiles_dir / "020.png")
        water_center_up = load_image(tiles_dir / "021.png")
        water_corner2 = load_image(tiles_dir / "022.png")
        water_center_right = load_image(tiles_dir / "024.png")
        water_corner3 = load_image(tiles_dir / "027.png")
        water_center_down = load_image(tiles_dir / "026.png")
        water_corner4 = load_image(tiles_dir / "025.png")
        water_center_left = load_image(tiles_dir / "023.png")
        road = load_image(tiles_dir / "003.png")
        road_corner1 = load_image(tiles_dir / "015.png")
        road_center_up = load_image(tiles_dir / "005.png")
        road_corner2 = load_image(tiles_dir / "012.png")
        road_center_right = load_image(tiles_dir / "008.png")
        road_corner3 = load_image(tiles_dir / "013.png")
        road_center_down = load_image(tiles_dir / "010.png")
        road_corner4 = load_image(tiles_dir / "014.png")
        road_center_left = load_image(tiles_dir / "007.png")
        water_external_corner1 = load_image(tiles_dir / "028.png")
        water_external_corner2 = load_image(tiles_dir / "029.png")
        water_external_corner3 = load_image(tiles_dir / "031.png")
        water_external_corner4 = load_image(tiles_dir / "030.png")
        dirt_ground = load_image(tiles_dir / "017.png")
        wood_floor = load_image(tiles_dir / "034.png")
        stairs_up = load_image(tiles_dir / "037.png")
        stairs_down = load_image(tiles_dir / "036.png")

        self.tile_grass = pygame.transform.scale(
            grass,
            (grass.get_width() * display_scale, grass.get_height() * display_scale),
        )
        self.tile_void = pygame.transform.scale(
            void,
            (void.get_width() * display_scale, void.get_height() * display_scale),
        )
        self.tile_water = pygame.transform.scale(
            water,
            (water.get_width() * display_scale, water.get_height() * display_scale),
        )
        self.tile_wall = pygame.transform.scale(
            wall,
            (wall.get_width() * display_scale, wall.get_height() * display_scale),
        )
        self.tile_tree = pygame.transform.scale(
            tree,
            (tree.get_width() * display_scale, tree.get_height() * display_scale),
        )
        self.tile_water_corner1 = pygame.transform.scale(
            water_corner1,
            (water_corner1.get_width() * display_scale, water_corner1.get_height() * display_scale),
        )
        self.tile_water_center_up = pygame.transform.scale(
            water_center_up,
            (water_center_up.get_width() * display_scale, water_center_up.get_height() * display_scale),
        )
        self.tile_water_corner2 = pygame.transform.scale(
            water_corner2,
            (water_corner2.get_width() * display_scale, water_corner2.get_height() * display_scale),
        )
        self.tile_water_center_right = pygame.transform.scale(
            water_center_right,
            (water_center_right.get_width() * display_scale, water_center_right.get_height() * display_scale),
        )
        self.tile_water_corner3 = pygame.transform.scale(
            water_corner3,
            (water_corner3.get_width() * display_scale, water_corner3.get_height() * display_scale),
        )
        self.tile_water_center_down = pygame.transform.scale(
            water_center_down,
            (water_center_down.get_width() * display_scale, water_center_down.get_height() * display_scale),
        )
        self.tile_water_corner4 = pygame.transform.scale(
            water_corner4,
            (water_corner4.get_width() * display_scale, water_corner4.get_height() * display_scale),
        )
        self.tile_water_center_left = pygame.transform.scale(
            water_center_left,
            (water_center_left.get_width() * display_scale, water_center_left.get_height() * display_scale),
        )
        self.tile_road = pygame.transform.scale(
            road,
            (road.get_width() * display_scale, road.get_height() * display_scale),
        )
        self.tile_road_corner1 = pygame.transform.scale(
            road_corner1,
            (road_corner1.get_width() * display_scale, road_corner1.get_height() * display_scale),
        )
        self.tile_road_center_up = pygame.transform.scale(
            road_center_up,
            (road_center_up.get_width() * display_scale, road_center_up.get_height() * display_scale),
        )
        self.tile_road_corner2 = pygame.transform.scale(
            road_corner2,
            (road_corner2.get_width() * display_scale, road_corner2.get_height() * display_scale),
        )
        self.tile_road_center_right = pygame.transform.scale(
            road_center_right,
            (road_center_right.get_width() * display_scale, road_center_right.get_height() * display_scale),
        )
        self.tile_road_corner3 = pygame.transform.scale(
            road_corner3,
            (road_corner3.get_width() * display_scale, road_corner3.get_height() * display_scale),
        )
        self.tile_road_center_down = pygame.transform.scale(
            road_center_down,
            (road_center_down.get_width() * display_scale, road_center_down.get_height() * display_scale),
        )
        self.tile_road_corner4 = pygame.transform.scale(
            road_corner4,
            (road_corner4.get_width() * display_scale, road_corner4.get_height() * display_scale),
        )
        self.tile_road_center_left = pygame.transform.scale(
            road_center_left,
            (road_center_left.get_width() * display_scale, road_center_left.get_height() * display_scale),
        )
        self.tile_water_external_corner1 = pygame.transform.scale(
            water_external_corner1,
            (water_external_corner1.get_width() * display_scale, water_external_corner1.get_height() * display_scale),
        )
        self.tile_water_external_corner2 = pygame.transform.scale(
            water_external_corner2,
            (water_external_corner2.get_width() * display_scale, water_external_corner2.get_height() * display_scale),
        )
        self.tile_water_external_corner3 = pygame.transform.scale(
            water_external_corner3,
            (water_external_corner3.get_width() * display_scale, water_external_corner3.get_height() * display_scale),
        )
        self.tile_water_external_corner4 = pygame.transform.scale(
            water_external_corner4,
            (water_external_corner4.get_width() * display_scale, water_external_corner4.get_height() * display_scale),
        )
        self.tile_dirt_ground = pygame.transform.scale(
            dirt_ground,
            (dirt_ground.get_width() * display_scale, dirt_ground.get_height() * display_scale),
        )
        self.tile_wood_floor = pygame.transform.scale(
            wood_floor,
            (wood_floor.get_width() * display_scale, wood_floor.get_height() * display_scale),
        ) 
        self.tile_stairs_up = pygame.transform.scale(
            stairs_up,
            (stairs_up.get_width() * display_scale, stairs_up.get_height() * display_scale),
        )
        self.tile_stairs_down = pygame.transform.scale(
            stairs_down,
            (stairs_down.get_width() * display_scale, stairs_down.get_height() * display_scale),
        )
        self.images = {
            ".": self.tile_grass,
            "V": self.tile_void,
            "~": self.tile_water,
            "#": self.tile_wall,
            "T": self.tile_tree,
            "1": self.tile_water_corner1,
            "2": self.tile_water_center_up,
            "3": self.tile_water_corner2,
            "4": self.tile_water_center_right,
            "5": self.tile_water_corner3,
            "6": self.tile_water_center_down,
            "7": self.tile_water_corner4,
            "8": self.tile_water_center_left,
            "9": self.tile_road,
            "A": self.tile_road_corner1,
            "B": self.tile_road_center_up,
            "C": self.tile_road_corner2,
            "D": self.tile_road_center_right,
            "E": self.tile_road_corner3,
            "F": self.tile_road_center_down,
            "G": self.tile_road_corner4,
            "H": self.tile_road_center_left,
            "I": self.tile_water_external_corner1,
            "J": self.tile_water_external_corner2,
            "K": self.tile_water_external_corner3,
            "L": self.tile_water_external_corner4,
            "M": self.tile_dirt_ground,
            "N": self.tile_wood_floor,
            "u": self.tile_stairs_up,
            "d": self.tile_stairs_down,
        }

        self.solid_tiles = {"#", "~", "V", "T", "1", "2", "3", "4", "5", "6", "7", "8", "I", "J", "K", "L"}

    def image_for(self, symbol: str):
        return self.images.get(symbol, self.tile_grass)