from monster import Monster


class Orc(Monster):
    def __init__(self, pos_px, tile_size: int, assets_dir, scale: int = 1):
        super().__init__(
            pos_px,
            tile_size,
            assets_dir,
            "orc_down_1.png",
            max_hp=5,
            scale=scale,
            aggro_tiles=9,
        )
        self.speed = 55 * max(1, scale)
