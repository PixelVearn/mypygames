from pathlib import Path

import pygame


# Asset-loading helpers.
# Keeping this in a separate file lets the rest of the game stay focused on gameplay.


def load_image(path: Path, size=None):
    """Load an image from disk.

    - If `size` is provided, the image is scaled to that size.
    - If the file can't be loaded, we return a magenta placeholder surface so the
      game can still run.
    """
    try:
        img = pygame.image.load(str(path)).convert_alpha()
        if size is not None:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        # Placeholder (magenta) makes missing assets very visible.
        if size is None:
            size = (32, 32)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 255))
        return surf
