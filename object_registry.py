from pathlib import Path

import pygame

from assets import load_image


class ObjectRegistry:
    def __init__(self, project_dir: Path, display_scale: int):
        self.display_scale = display_scale
        self.objects_dir = project_dir / "objects"
        tiles_dir = project_dir / "tiles"

        self.blocking_objects = {"h", "t", "|", "c", "C"}

        door = load_image(self.objects_dir / "door.png")
        coin = load_image(self.objects_dir / "silverCoin1.png")
        key = load_image(self.objects_dir / "key.png")
        potion = load_image(self.objects_dir / "potion_red.png")
        house = load_image(tiles_dir / "033.png")
        table = load_image(tiles_dir / "035.png")
        chest_closed = load_image(self.objects_dir / "chest_close.png")
        chest_open = load_image(self.objects_dir / "chest_open.png")
        blueheart = load_image(self.objects_dir / "blueheart.png")

        self.images: dict[str, pygame.Surface] = {
            "|": pygame.transform.scale(door, (door.get_width() * display_scale, door.get_height() * display_scale)),
            "$": pygame.transform.scale(coin, (coin.get_width() * display_scale, coin.get_height() * display_scale)),
            "k": pygame.transform.scale(key, (key.get_width() * display_scale, key.get_height() * display_scale)),
            "p": pygame.transform.scale(potion, (potion.get_width() * display_scale, potion.get_height() * display_scale)),
            "h": pygame.transform.scale(house, (house.get_width() * display_scale, house.get_height() * display_scale)),
            "t": pygame.transform.scale(table, (table.get_width() * display_scale, table.get_height() * display_scale)),
            "c": pygame.transform.scale(
                chest_closed,
                (chest_closed.get_width() * display_scale, chest_closed.get_height() * display_scale),
            ),
            "C": pygame.transform.scale(
                chest_open,
                (chest_open.get_width() * display_scale, chest_open.get_height() * display_scale),
            ),
            "b": pygame.transform.scale(
                blueheart,
                (blueheart.get_width() * display_scale, blueheart.get_height() * display_scale),
            ),
        }

    def is_blocking(self, symbol: str):
        return symbol in self.blocking_objects

    def image_for(self, symbol: str):
        return self.images.get(symbol)