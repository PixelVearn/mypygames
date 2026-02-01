from pathlib import Path

import pygame

from assets import load_image
from pathfinding import astar


class Monster:
    # Very simple enemy: just sits in place with HP.
    def __init__(
        self,
        pos_px,
        tile_size: int,
        assets_dir: Path,
        sprite_name: str,
        max_hp: int = 3,
        scale: int = 1,
        aggro_tiles: int = 7,
    ):
        self.tile_size = tile_size
        self.scale = scale
        self.speed = 55 * max(1, scale)
        self.aggro_radius_px = aggro_tiles * tile_size
        self.max_hp = max_hp
        self.hp = max_hp

        self.dying = False
        self._dying_t = 0.0
        self.dying_time = 0.60

        # Animation (2 frames)
        self._anim_t = 0.0
        self._anim_i = 0
        self.anim_frame_time = 0.20

        self.hit_flash_time = 0.25
        self._hit_t = 0.0

        # HP bar visibility (only show after being hit)
        self._hp_bar_visible_time = 2.5  # Show HP bar for 2.5 seconds after hit
        self._hp_bar_t = 0.0

        # Pathfinding
        self._path = []
        self._repath_t = 0.0
        self.repath_interval = 0.40
        self._last_goal = None

        # Use a small hitbox near the bottom (similar idea to the player).
        hb_w = int(tile_size * 0.75)
        hb_h = int(tile_size * 0.50)
        self.rect = pygame.Rect(0, 0, hb_w, hb_h)

        sprite_x, sprite_y = pos_px
        self.rect.midbottom = (sprite_x + tile_size // 2, sprite_y + tile_size)

        # Float position for smooth movement.
        self.pos = pygame.Vector2(self.rect.topleft)

        self._knock_vel = pygame.Vector2(0, 0)
        self._knock_t = 0.0

        # Try to load 2 frames if your assets have _1.png / _2.png naming.
        # Example: bat_down_1.png + bat_down_2.png
        self.direction = "down"

        def load_two_frame(base_name_1: str):
            p1 = assets_dir / base_name_1
            if base_name_1.endswith("_1.png"):
                p2 = assets_dir / base_name_1.replace("_1.png", "_2.png")
            else:
                p2 = assets_dir / base_name_1

            img1 = load_image(p1)
            img2 = load_image(p2)
            return [
                pygame.transform.scale(img1, (img1.get_width() * self.scale, img1.get_height() * self.scale)),
                pygame.transform.scale(img2, (img2.get_width() * self.scale, img2.get_height() * self.scale)),
            ]

        # Always load the provided direction (usually "down")
        down_name = sprite_name
        down_frames = load_two_frame(down_name)

        # If you have directional sprites (orc_left_1.png, orc_up_1.png, etc.), load them.
        # Otherwise, fall back to down frames.
        def candidate_name(dir_name: str):
            return down_name.replace("_down_", f"_{dir_name}_")

        def try_load_dir(dir_name: str):
            name = candidate_name(dir_name)
            # Only switch to that direction if at least the first frame exists.
            if (assets_dir / name).exists():
                return load_two_frame(name)
            return down_frames

        self.frames = {
            "down": down_frames,
            "up": try_load_dir("up"),
            "left": try_load_dir("left"),
            "right": try_load_dir("right"),
        }

    def _move_and_collide(self, delta: pygame.Vector2, colliders_for_rect):
        self.pos.x += delta.x
        self.rect.x = int(self.pos.x)
        for c in colliders_for_rect(self.rect):
            if self.rect.colliderect(c):
                if delta.x > 0:
                    self.rect.right = c.left
                elif delta.x < 0:
                    self.rect.left = c.right
                self.pos.x = float(self.rect.x)

        self.pos.y += delta.y
        self.rect.y = int(self.pos.y)
        for c in colliders_for_rect(self.rect):
            if self.rect.colliderect(c):
                if delta.y > 0:
                    self.rect.bottom = c.top
                elif delta.y < 0:
                    self.rect.top = c.bottom
                self.pos.y = float(self.rect.y)

    def apply_knockback(self, direction: pygame.Vector2, strength: float = 220.0, time: float = 0.12):
        if self.dying:
            return
        if direction.length_squared() <= 0:
            return
        self._knock_vel = direction.normalize() * strength
        self._knock_t = max(self._knock_t, time)

    def update(self, dt: float, player_rect: pygame.Rect, colliders_for_rect, tile_w: int, tile_h: int, is_blocked_tile):
        # Animate even while idle.
        self._anim_t += dt
        if self._anim_t >= self.anim_frame_time:
            self._anim_t = 0.0
            self._anim_i = 1 - self._anim_i

        if self._hit_t > 0:
            self._hit_t = max(0.0, self._hit_t - dt)

        if self._hp_bar_t > 0:
            self._hp_bar_t = max(0.0, self._hp_bar_t - dt)

        if self.dying:
            self._dying_t += dt
            return

        if self._knock_t > 0:
            self._knock_t = max(0.0, self._knock_t - dt)
            self._move_and_collide(self._knock_vel * dt, colliders_for_rect)
            if self._knock_t > 0:
                return

        # Only chase the player once they're close enough.
        to_player = pygame.Vector2(player_rect.center) - pygame.Vector2(self.rect.center)
        chasing = to_player.length() <= self.aggro_radius_px

        move = pygame.Vector2(0, 0)
        if chasing and to_player.length_squared() > 0:
            # A* path on the tile grid.
            start = (int(self.rect.centerx) // self.tile_size, int(self.rect.centery) // self.tile_size)
            goal = (int(player_rect.centerx) // self.tile_size, int(player_rect.centery) // self.tile_size)

            self._repath_t = max(0.0, self._repath_t - dt)
            if self._repath_t <= 0 or self._last_goal != goal or not self._path:
                self._repath_t = self.repath_interval
                self._last_goal = goal
                self._path = astar(start, goal, is_blocked_tile, tile_w, tile_h)

            if self._path:
                next_tile = self._path[0]
                tx, ty = next_tile
                target = pygame.Vector2((tx + 0.5) * self.tile_size, (ty + 0.5) * self.tile_size)
                to_target = target - pygame.Vector2(self.rect.center)

                # Pop tile when close enough to its center.
                if to_target.length_squared() <= (self.tile_size * 0.15) ** 2:
                    self._path.pop(0)
                else:
                    move = to_target.normalize()
            else:
                # Fallback if no path found.
                move = to_player.normalize()

        if move.length_squared() > 0:
            if abs(move.x) > abs(move.y):
                self.direction = "right" if move.x > 0 else "left"
            else:
                self.direction = "down" if move.y > 0 else "up"

        delta = move * self.speed * dt
        self._move_and_collide(delta, colliders_for_rect)

        # Optional: prevent monsters overlapping the player (simple push-out).
        if self.rect.colliderect(player_rect):
            overlap = pygame.Vector2(self.rect.center) - pygame.Vector2(player_rect.center)
            if overlap.length_squared() > 0:
                push = overlap.normalize()
                self.pos += push * (self.speed * dt)
                self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def is_dead(self):
        return self.dying and self._dying_t >= self.dying_time

    def is_dying(self):
        return self.dying

    def take_damage(self, amount: int):
        if self.dying:
            return False
        self.hp = max(0, self.hp - amount)
        self._hit_t = self.hit_flash_time
        self._hp_bar_t = self._hp_bar_visible_time  # Show HP bar when hit
        if self.hp <= 0:
            self.dying = True
            self._dying_t = 0.0
            self._hit_t = 0.0
            self._hp_bar_t = 0.0  # Hide HP bar when dying
        return True

    def get_draw_pos(self):
        # Draw sprite aligned to its hitbox.
        img = self.frames[self.direction][self._anim_i]
        x = self.rect.centerx - img.get_width() // 2
        y = self.rect.bottom - img.get_height()
        return x, y

    def draw(self, screen: pygame.Surface, camera_offset: pygame.Vector2):
        x, y = self.get_draw_pos()
        img = self.frames[self.direction][self._anim_i]
        # More visible retro feedback: blink while hit, otherwise draw with slight alpha.
        if self._hit_t > 0 and not self.dying:
            if int(self._hit_t * 25) % 2 == 0:
                return
            img = img.copy()
            img.set_alpha(170)
        if self.dying:
            t = 0.0
            if self.dying_time > 0:
                t = min(1.0, self._dying_t / self.dying_time)
            alpha = max(0, int(255 * (1.0 - t)))
            img = img.copy()
            img.set_alpha(alpha)

        screen.blit(img, (x - int(camera_offset.x), y - int(camera_offset.y)))

        # HP bar: only show after being hit, with smooth fade out
        if not self.dying and self._hp_bar_t > 0:
            bar_w = self.tile_size
            bar_h = max(3, self.tile_size // 4)
            bar_x = x - int(camera_offset.x)
            bar_y = (y - max(6, self.tile_size // 3)) - int(camera_offset.y)
            
            # Calculate alpha for smooth fade out in last 0.5 seconds
            alpha = 255
            fade_duration = 0.5
            if self._hp_bar_t < fade_duration:
                alpha = int(255 * (self._hp_bar_t / fade_duration))
            
            # Create surfaces with alpha for smooth fade
            bg_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            bg_surf.fill((40, 40, 40, alpha))
            screen.blit(bg_surf, (bar_x, bar_y))
            
            if self.max_hp > 0:
                fill_w = int(bar_w * (self.hp / self.max_hp))
                fill_surf = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
                fill_surf.fill((200, 50, 50, alpha))
                screen.blit(fill_surf, (bar_x, bar_y))