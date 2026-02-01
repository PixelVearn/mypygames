import pygame

from pathfinding import inflate_blocked


class WorldMap:
    def __init__(
        self,
        rows: list[str],
        tile_size: int,
        solid_tiles: set[str],
        inflate_margin: int = 1,
        objects: dict[tuple[int, int], str] | None = None,
    ):
        self.rows = rows
        self.tile_size = tile_size
        self.solid_tiles = solid_tiles
        self.objects = objects or {}

        self.h = len(rows)
        self.w = len(rows[0]) if self.h > 0 else 0

        self.inflate_margin = inflate_margin
        self.blocking_objects = {"h", "t", "|", "c", "C"}
        self.rebuild_blocked()

    def rebuild_blocked(self):
        base_blocked = set()
        for ty in range(self.h):
            row = self.rows[ty]
            for tx in range(self.w):
                if row[tx] in self.solid_tiles:
                    base_blocked.add((tx, ty))

        for (tx, ty), obj in self.objects.items():
            if obj in self.blocking_objects:
                base_blocked.add((tx, ty))

        self.inflated_blocked = inflate_blocked(base_blocked, self.w, self.h, margin=self.inflate_margin)

    @property
    def pixel_width(self):
        return self.w * self.tile_size

    @property
    def pixel_height(self):
        return self.h * self.tile_size

    def is_blocked_tile(self, tx: int, ty: int):
        return (tx, ty) in self.inflated_blocked

    def colliders_for_rect(self, r: pygame.Rect):
        left = max(0, r.left // self.tile_size)
        right = min(self.w - 1, (r.right - 1) // self.tile_size)
        top = max(0, r.top // self.tile_size)
        bottom = min(self.h - 1, (r.bottom - 1) // self.tile_size)

        colliders = []
        for ty in range(top, bottom + 1):
            row = self.rows[ty]
            for tx in range(left, right + 1):
                t = row[tx]
                if t in self.solid_tiles:
                    colliders.append(pygame.Rect(tx * self.tile_size, ty * self.tile_size, self.tile_size, self.tile_size))

                if (tx, ty) in self.objects and self.objects[(tx, ty)] in self.blocking_objects:
                    colliders.append(pygame.Rect(tx * self.tile_size, ty * self.tile_size, self.tile_size, self.tile_size))
        return colliders

    def draw(self, screen: pygame.Surface, camera_offset: pygame.Vector2, tileset, object_registry=None):
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        start_tx = max(0, int(camera_offset.x) // self.tile_size)
        end_tx = min(self.w - 1, (int(camera_offset.x) + screen_w) // self.tile_size + 1)
        start_ty = max(0, int(camera_offset.y) // self.tile_size)
        end_ty = min(self.h - 1, (int(camera_offset.y) + screen_h) // self.tile_size + 1)

        for ty in range(start_ty, end_ty + 1):
            row = self.rows[ty]
            for tx in range(start_tx, end_tx + 1):
                ch = row[tx]
                img = tileset.image_for(ch)
                x = tx * self.tile_size - int(camera_offset.x)
                y = ty * self.tile_size - int(camera_offset.y)
                screen.blit(img, (x, y))

                obj = self.objects.get((tx, ty))
                if obj is not None:
                    obj_img = None
                    if object_registry is not None:
                        obj_img = object_registry.image_for(obj)
                    if obj_img is None:
                        obj_img = tileset.image_for(obj)
                    screen.blit(obj_img, (x, y))