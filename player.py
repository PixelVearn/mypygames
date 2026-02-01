from pathlib import Path

import pygame

from assets import load_image


class Player:
    # Player handles:
    # - reading keyboard input
    # - moving the player rect
    # - stopping movement when colliding with solid tiles
    # - choosing an animation frame based on direction
    def __init__(self, pos_px, tile_size: int, assets_dir: Path, scale: int = 1):
        self.tile_size = tile_size
        self.scale = scale
        # Speed in pixels/sec. Tuned for 16x16 tiles.
        self.speed = 96 * max(1, scale)

        self.max_hp = 6
        self.hp = self.max_hp
        self.invuln_time = 0.8
        self._invuln_t = 0.0

        # Attack tuning (in seconds)
        self.attack_frame_time = 0.09
        self.attack_cooldown = 0.25
        self._attack_t = 0.0
        self._attack_i = 0
        self._attack_cd_t = 0.0
        self.attacking = False
        self.attack_dir = "down"
        self.attack_damage_applied = False

        # We use a small hitbox for collisions (more realistic than colliding with the full sprite).
        # This hitbox is positioned near the player's feet.
        hb_w = int(tile_size * 0.45)
        hb_h = int(tile_size * 0.30)
        self.rect = pygame.Rect(0, 0, hb_w, hb_h)

        # `pos_px` is treated as the *sprite* top-left spawn.
        # Place the hitbox so it sits at the bottom of the sprite.
        sprite_x, sprite_y = pos_px
        self.rect.midbottom = (sprite_x + tile_size // 2, sprite_y + tile_size)

        # Keep a float position so movement doesn't jitter from int rounding.
        self.pos = pygame.Vector2(self.rect.topleft)

        self.direction = "down"
        self._anim_t = 0.0
        self._anim_i = 0

        # Load 3 frames for each direction.
        # If a file is missing, load_image returns a placeholder so the game still runs.
        self.frames = {
            "down": [
                load_image(assets_dir / "down0.png"),
                load_image(assets_dir / "down1.png"),
                load_image(assets_dir / "down2.png"),
            ],
            "up": [
                load_image(assets_dir / "up0.png"),
                load_image(assets_dir / "up1.png"),
                load_image(assets_dir / "up2.png"),
            ],
            "left": [
                load_image(assets_dir / "left0.png"),
                load_image(assets_dir / "left1.png"),
                load_image(assets_dir / "left2.png"),
            ],
            "right": [
                load_image(assets_dir / "right0.png"),
                load_image(assets_dir / "right1.png"),
                load_image(assets_dir / "right2.png"),
            ],
        }

        # Attack animations (3 frames each direction).
        # Your filenames look like: $rightattmainchar1.png, $rightattmainchar2.png, $rightattmainchar3.png
        self.attack_frames = {
            "down": [
                load_image(assets_dir / "$downattmainchar1.png"),
                load_image(assets_dir / "$downattmainchar2.png"),
                load_image(assets_dir / "$downattmainchar3.png"),
            ],
            "up": [
                load_image(assets_dir / "$upattmainchar1.png"),
                load_image(assets_dir / "$upattmainchar2.png"),
                load_image(assets_dir / "$upattmainchar3.png"),
            ],
            "left": [
                load_image(assets_dir / "$leftattmainchar1.png"),
                load_image(assets_dir / "$leftattmainchar2.png"),
                load_image(assets_dir / "$leftattmainchar3.png"),
            ],
            "right": [
                load_image(assets_dir / "$rightattmainchar1.png"),
                load_image(assets_dir / "$rightattmainchar2.png"),
                load_image(assets_dir / "$rightattmainchar3.png"),
            ],
        }

        for k, imgs in self.frames.items():
            # Pixel-art friendly scaling: keep original proportions and scale by an integer factor.
            self.frames[k] = [
                pygame.transform.scale(i, (i.get_width() * self.scale, i.get_height() * self.scale)) for i in imgs
            ]

        for k, imgs in self.attack_frames.items():
            # Attack frames are wider than 16x16, so we must NOT force them into a square.
            self.attack_frames[k] = [
                pygame.transform.scale(i, (i.get_width() * self.scale, i.get_height() * self.scale)) for i in imgs
            ]

    def current_image(self):
        if self.attacking:
            return self.attack_frames[self.attack_dir][self._attack_i]
        return self.frames[self.direction][self._anim_i]

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount: int):
        if self._invuln_t > 0 or self.hp <= 0:
            return False
        self.hp = max(0, self.hp - amount)
        self._invuln_t = self.invuln_time
        return True

    def get_draw_image(self):
        img = self.current_image()
        if self._invuln_t <= 0:
            return img

        # Retro flicker: alternate visibility/alpha.
        if int(self._invuln_t * 20) % 2 == 0:
            return None
        temp = img.copy()
        temp.set_alpha(140)
        return temp

    def get_draw_pos(self):
        # Convert hitbox position to sprite position.
        # Important: some attack frames are wider (ex: 32x16) than the walk frames (16x16).
        # If we simply center the wider image, the character looks like they "step" sideways.
        # To avoid that, we anchor attack frames so the *body* stays where the normal sprite is.
        img = self.current_image()

        # Use the normal (walk) frame width as the "body width" reference.
        base_dir = self.attack_dir if self.attacking else self.direction
        normal_w = self.frames[base_dir][0].get_width()
        normal_h = self.frames[base_dir][0].get_height()

        # Normal sprite position (body anchored): centered on hitbox.
        normal_x = self.rect.centerx - normal_w // 2

        if self.attacking and img.get_width() != normal_w:
            # Right-attack sprites extend to the right: keep their left edge fixed.
            if self.attack_dir == "right":
                x = normal_x
            # Left-attack sprites extend to the left: keep their right edge fixed.
            elif self.attack_dir == "left":
                x = normal_x + normal_w - img.get_width()
            else:
                x = self.rect.centerx - img.get_width() // 2
        else:
            x = self.rect.centerx - img.get_width() // 2

        # For Y, we normally align feet by matching the bottom.
        # But if an attack frame is taller (ex: extra pixels below the feet on down-attack),
        # aligning to the attack bottom can make the body appear to "step".
        # So for down-attacks with different height, anchor using the normal (walk) height.
        if self.attacking and self.attack_dir == "down" and img.get_height() != normal_h:
            y = self.rect.bottom - normal_h
        else:
            y = self.rect.bottom - img.get_height()
        return x, y

    def start_attack(self):
        # Start an attack if we're not already attacking and the cooldown is finished.
        if self.attacking or self._attack_cd_t > 0:
            return False
        self.attacking = True
        self.attack_dir = self.direction
        self._attack_t = 0.0
        self._attack_i = 0
        self.attack_damage_applied = False
        return True

    def attack_hitbox_active(self):
        # Make the hitbox active during the middle of the animation.
        # (This feels more natural than dealing damage instantly on key press.)
        return self.attacking and self._attack_t >= self.attack_frame_time and self._attack_t <= (self.attack_frame_time * 2)

    def get_attack_hitbox(self):
        # A rectangle in front of the player hitbox.
        # Make the hitbox a bit larger and pushed forward so you don't need to be pixel-perfect close.
        size_w = int(self.tile_size * 0.90)
        size_h = int(self.tile_size * 0.70)
        reach = int(self.tile_size * 0.35)

        if self.attack_dir == "right":
            return pygame.Rect(self.rect.right + reach, self.rect.centery - size_h // 2, size_w, size_h)
        if self.attack_dir == "left":
            return pygame.Rect(self.rect.left - size_w - reach, self.rect.centery - size_h // 2, size_w, size_h)
        if self.attack_dir == "up":
            return pygame.Rect(self.rect.centerx - size_w // 2, self.rect.top - size_h - reach, size_w, size_h)
        return pygame.Rect(self.rect.centerx - size_w // 2, self.rect.bottom + reach, size_w, size_h)

    def handle_input(self):
        # Convert keyboard state into a direction vector (-1/0/1 on x/y).
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1

        run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        return pygame.Vector2(dx, dy), run

    def update(self, dt: float, colliders_for_rect):
        # `dt` is seconds since last frame (makes movement frame-rate independent).
        # `colliders_for_rect(rect)` returns a list of solid tile rects near the player.
        if self._invuln_t > 0:
            self._invuln_t = max(0.0, self._invuln_t - dt)

        if self._attack_cd_t > 0:
            self._attack_cd_t = max(0.0, self._attack_cd_t - dt)

        # Attack state: we lock movement, only play the attack animation.
        if self.attacking:
            self._attack_t += dt
            self._attack_i = min(2, int(self._attack_t // self.attack_frame_time))
            if self._attack_t >= (self.attack_frame_time * 3):
                self.attacking = False
                self._attack_cd_t = self.attack_cooldown
            return

        move, run = self.handle_input()
        moving = move.length_squared() > 0
        if moving:
            # Pick which direction animation to show.
            if move.x < 0:
                self.direction = "left"
            elif move.x > 0:
                self.direction = "right"
            elif move.y < 0:
                self.direction = "up"
            elif move.y > 0:
                self.direction = "down"

        if moving:
            move = move.normalize()
            speed = self.speed * (1.5 if run else 1.0)

            delta = move * speed * dt

            # Move X (float) then resolve X collisions.
            self.pos.x += delta.x
            self.rect.x = int(self.pos.x)
            for c in colliders_for_rect(self.rect):
                if self.rect.colliderect(c):
                    if delta.x > 0:
                        self.rect.right = c.left
                    elif delta.x < 0:
                        self.rect.left = c.right
                    self.pos.x = float(self.rect.x)

            # Move Y (float) then resolve Y collisions.
            self.pos.y += delta.y
            self.rect.y = int(self.pos.y)
            for c in colliders_for_rect(self.rect):
                if self.rect.colliderect(c):
                    if delta.y > 0:
                        self.rect.bottom = c.top
                    elif delta.y < 0:
                        self.rect.top = c.bottom
                    self.pos.y = float(self.rect.y)

            # Advance animation while walking.
            self._anim_t += dt
            if self._anim_t >= 0.12:
                self._anim_t = 0.0
                self._anim_i = (self._anim_i + 1) % len(self.frames[self.direction])
        else:
            # When idle, always show the first frame.
            self._anim_t = 0.0
            self._anim_i = 0