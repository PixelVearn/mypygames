import pygame


class Camera:
    # The camera stores an offset (in pixels) that we subtract when drawing.
    # If the player is at world position (x, y), we draw them at (x - offset.x, y - offset.y).
    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.offset = pygame.Vector2(0, 0)

    def update(self, target_rect: pygame.Rect, world_px_w: int, world_px_h: int):
        # Center the camera on the target (player) by moving the top-left corner.
        ox = target_rect.centerx - self.screen_w // 2
        oy = target_rect.centery - self.screen_h // 2

        # Clamp so the camera never shows outside the world.
        ox = max(0, min(ox, world_px_w - self.screen_w))
        oy = max(0, min(oy, world_px_h - self.screen_h))
        self.offset.update(ox, oy)