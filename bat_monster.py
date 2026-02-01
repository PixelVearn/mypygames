from monster import Monster


class Bat(Monster):
    def __init__(self, pos_px, tile_size: int, assets_dir, scale: int = 1):
        super().__init__(
            pos_px,
            tile_size,
            assets_dir,
            "bat_down_1.png",
            max_hp=2,
            scale=scale,
            aggro_tiles=6,
        )
        self.speed = 80 * max(1, scale)
