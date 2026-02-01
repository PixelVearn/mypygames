from monster import Monster


class GreenSlime(Monster):
    def __init__(self, pos_px, tile_size: int, assets_dir, scale: int = 1):
        super().__init__(
            pos_px,
            tile_size,
            assets_dir,
            "greenslime_down_1.png",
            max_hp=3,
            scale=scale,
            aggro_tiles=7,
        )
        self.speed = 45 * max(1, scale)
