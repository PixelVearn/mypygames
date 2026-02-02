from pathlib import Path

import random

import pygame

from asset_setter import spawn_entities_from_map
from camera import Camera
from event_handler import EventHandler
from map_loader import load_map_file
from object_registry import ObjectRegistry
from sound_manager import SoundManager
from tileset import TileSet
from ui import UI
from world_map import WorldMap


class GamePanel:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

        pygame.init()

        base_tile = 16
        self.display_scale = 3
        self.tile_size = base_tile * self.display_scale

        self.screen_w, self.screen_h = self.tile_size * 16, self.tile_size * 12
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Endless Dungeons_pygame")

        self.clock = pygame.time.Clock()
        self.ui = UI()

        self.map_dir = self.project_dir / "maps"
        map_file = self.map_dir / "map.txt"
        if not map_file.exists():
            raise FileNotFoundError("maps/map.txt not found. Create it to play.")

        self.map_files = sorted(p for p in self.map_dir.glob("*.txt") if p.name not in {"house.txt", "cave.txt"})
        if not self.map_files:
            self.map_files = [map_file]

        try:
            self.current_map_index = next(i for i, p in enumerate(self.map_files) if p.name == "map.txt")
        except StopIteration:
            self.current_map_index = 0

        self.tileset = TileSet(self.project_dir / "tiles", self.display_scale)
        self.object_registry = ObjectRegistry(self.project_dir, self.display_scale)
        self.raw_rows = load_map_file(self.map_files[self.current_map_index])

        self.sound = SoundManager(self.project_dir / "sound")
        self.sound.play_music()

        self.camera = Camera(self.screen_w, self.screen_h)

        self.world = None
        self.player = None
        self.monsters = []
        self.game_over = False
        self.paused = False
        self._gameover_sfx_played = False
        
        self.victory = False
        self.monsters_killed = 0
        self.total_coins_collected = 0

        self.inventory_open = False
        self.inventory: dict[str, int] = {}

        self._monster_drop_done: set[int] = set()

        # EventHandler owns all transition state and logic.
        self.events = EventHandler(self)

        self.reset_game()

    # ------------------------------------------------------------------
    # game state
    # ------------------------------------------------------------------
    def reset_game(self, spawn_tile: tuple[int, int] | None = None):
        if self.events.in_cave:
            map_name = "cave.txt"
        elif self.events.in_interior:
            map_name = "house.txt"
        else:
            map_name = self.map_files[self.current_map_index].name

        cleaned_rows, p, ms, objects = spawn_entities_from_map(
            self.project_dir,
            self.raw_rows,
            self.tile_size,
            self.display_scale,
            map_name,
            spawn_tile=spawn_tile,
        )
        self.world = WorldMap(cleaned_rows, self.tile_size, self.tileset.solid_tiles, inflate_margin=1, objects=objects)
        self.player = p
        self.monsters = ms
        self._monster_drop_done = set()
        self.game_over = False
        self.paused = False
        self._gameover_sfx_played = False
        self.victory = False
        
        # Play appropriate music based on location
        if self.events.in_cave:
            self.sound.play_cave_music()
        else:
            self.sound.play_music()

    # ------------------------------------------------------------------
    # helpers (used by EventHandler via self.gp)
    # ------------------------------------------------------------------
    def _fade(self, mode: str, duration: float = 0.22):
        if duration <= 0:
            return
        overlay = pygame.Surface((self.screen_w, self.screen_h))
        overlay.fill((0, 0, 0))

        t = 0.0
        while t < duration:
            dt = self.clock.tick(60) / 1000.0
            t += dt
            a = min(255, int(255 * (t / duration)))
            if mode == "in":
                a = 255 - a
            overlay.set_alpha(a)

            self.screen.fill((0, 0, 0))
            if self.world is not None:
                self.world.draw(self.screen, self.camera.offset, self.tileset, object_registry=self.object_registry)
                for m in self.monsters:
                    m.draw(self.screen, self.camera.offset)

                if self.player is not None:
                    px, py = self.player.get_draw_pos()
                    pimg = self.player.get_draw_image()
                    if pimg is not None:
                        self.screen.blit(
                            pimg,
                            (px - int(self.camera.offset.x), py - int(self.camera.offset.y)),
                        )

            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()

    def _adjacent_object_tile(self, valid: set[str]):
        tile = self._tile_under_player()
        if tile is None:
            return None
        tx, ty = tile
        for nx, ny in ((tx, ty), (tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1)):
            obj = self.world.objects.get((nx, ny))
            if obj in valid:
                return nx, ny
        return None

    def _adjacent_house_tile(self):
        tile = self._tile_under_player()
        if tile is None:
            return None
        tx, ty = tile
        for nx, ny in ((tx, ty), (tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1)):
            if (nx, ny) in self.world.objects and self.world.objects[(nx, ny)] == "h":
                return nx, ny
        return None

    def _tile_under_player(self):
        tx = int(self.player.rect.centerx) // self.tile_size
        ty = int(self.player.rect.centery) // self.tile_size
        if tx < 0 or ty < 0 or tx >= self.world.w or ty >= self.world.h:
            return None
        return tx, ty

    def _find_tile(self, symbol: str):
        for ty, row in enumerate(self.raw_rows):
            for tx, ch in enumerate(row):
                if ch == symbol:
                    return tx, ty
        return None

    # ------------------------------------------------------------------
    # pickups & drops
    # ------------------------------------------------------------------
    def _collect_pickups_under_player(self):
        tile = self._tile_under_player()
        if tile is None:
            return
        sym = self.world.objects.get(tile)
        if sym not in {"$", "k", "p", "b"}:
            return

        self.world.objects.pop(tile, None)
        
        if sym == "b":
            # Blue heart collected - victory!
            self.victory = True
            self.game_over = True
            self.sound.stop_music()
            self.sound.play_fanfare()
            return
        
        self.sound.play_pickup()
        if sym == "$":
            self.inventory["coin"] = self.inventory.get("coin", 0) + 1
            self.total_coins_collected += 1
        elif sym == "k":
            self.inventory["key"] = self.inventory.get("key", 0) + 1
        elif sym == "p":
            self.inventory["potion"] = self.inventory.get("potion", 0) + 1

    def _spawn_drop_at(self, tx: int, ty: int):
        if (tx, ty) in self.world.objects:
            return False
        r = random.random()
        if r < 0.70:
            self.world.objects[(tx, ty)] = "$"
        else:
            self.world.objects[(tx, ty)] = "p"
        return True

    def _try_spawn_monster_drops(self):
        for m in self.monsters:
            mid = id(m)
            if mid in self._monster_drop_done:
                continue
            if not m.is_dead():
                continue

            tx = int(m.rect.centerx) // self.tile_size
            ty = int(m.rect.centery) // self.tile_size
            if 0 <= tx < self.world.w and 0 <= ty < self.world.h:
                self._spawn_drop_at(tx, ty)
            self._monster_drop_done.add(mid)

    # ------------------------------------------------------------------
    # main loop
    # ------------------------------------------------------------------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    if not self.game_over:
                        self.paused = not self.paused
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    if self.inventory_open:
                        self.inventory_open = False
                    elif not self.game_over and not self.paused:
                        self.inventory_open = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    if not self.game_over and not self.paused:
                        if self.inventory.get("potion", 0) > 0 and self.player.hp > 0:
                            self.inventory["potion"] -= 1
                            if self.inventory["potion"] <= 0:
                                self.inventory.pop("potion", None)
                            self.player.hp = min(self.player.max_hp, self.player.hp + 2)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    if not self.game_over and not self.paused and not self.inventory_open:
                        self.events.handle_key_event(event.key)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not self.game_over and not self.paused and not self.inventory_open:
                        if self.player.start_attack():
                            self.sound.play_swing()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    if self.game_over:
                        # Reset to the main map and reset all stats
                        self.monsters_killed = 0
                        self.total_coins_collected = 0
                        self.inventory.clear()
                        self.events.reset()  # This now properly clears ALL event handler state
                        self.current_map_index = 0
                        self.raw_rows = load_map_file(self.map_files[self.current_map_index])
                        self.reset_game()

            if not self.game_over and not self.paused and not self.inventory_open:
                self.player.update(dt, self.world.colliders_for_rect)
                self.camera.update(self.player.rect, self.world.pixel_width, self.world.pixel_height)

                self._collect_pickups_under_player()

                # EventHandler: per-frame tile checks (stairs, house exit gap)
                self.events.update()
                self.events.flush_pending()

                for m in self.monsters:
                    m.update(dt, self.player.rect, self.world.colliders_for_rect, self.world.w, self.world.h, self.world.is_blocked_tile)

                for m in self.monsters:
                    if m.is_dying():
                        continue
                    dist = pygame.Vector2(m.rect.center).distance_to(self.player.rect.center)
                    if dist <= self.tile_size * 0.75:
                        if self.player.take_damage(1):
                            self.sound.play_damage()

                for m in self.monsters:
                    if m.is_dying():
                        continue
                    if self.player.rect.colliderect(m.rect):
                        overlap = pygame.Vector2(self.player.rect.center) - pygame.Vector2(m.rect.center)
                        if overlap.length_squared() > 0:
                            push = overlap.normalize()
                            self.player.pos += push * (self.player.speed * dt)
                            self.player.rect.topleft = (int(self.player.pos.x), int(self.player.pos.y))
                            for c in self.world.colliders_for_rect(self.player.rect):
                                if self.player.rect.colliderect(c):
                                    self.player.pos -= push * (self.player.speed * dt)
                                    self.player.rect.topleft = (int(self.player.pos.x), int(self.player.pos.y))
                                    break

                if not self.player.is_alive():
                    self.game_over = True
                    self.paused = False
                    if not self._gameover_sfx_played:
                        self.sound.stop_music()
                        self.sound.play_gameover()
                        self._gameover_sfx_played = True

            # Drops are spawned once monsters finish dying.
            self._try_spawn_monster_drops()

            if (
                not self.game_over
                and not self.paused
                and not self.inventory_open
                and self.player.attack_hitbox_active()
                and not self.player.attack_damage_applied
            ):
                hitbox = self.player.get_attack_hitbox()
                for m in self.monsters:
                    if hitbox.colliderect(m.rect):
                        if m.take_damage(1):
                            knock_dir = pygame.Vector2(m.rect.center) - pygame.Vector2(self.player.rect.center)
                            m.apply_knockback(knock_dir)
                            self.sound.play_hitmonster()
                self.player.attack_damage_applied = True

            if not self.paused:
                before_count = len(self.monsters)
                self.monsters = [m for m in self.monsters if not m.is_dead()]
                after_count = len(self.monsters)
                self.monsters_killed += (before_count - after_count)

            self.screen.fill((0, 0, 0))
            self.world.draw(self.screen, self.camera.offset, self.tileset, object_registry=self.object_registry)

            for m in self.monsters:
                m.draw(self.screen, self.camera.offset)

            px, py = self.player.get_draw_pos()
            pimg = self.player.get_draw_image()
            if pimg is not None:
                self.screen.blit(
                    pimg,
                    (px - int(self.camera.offset.x), py - int(self.camera.offset.y)),
                )

            self.ui.draw(
                self.screen,
                self.screen_w,
                self.screen_h,
                player_hp=self.player.hp,
                player_max_hp=self.player.max_hp,
                paused=self.paused,
                game_over=self.game_over,
                inventory_open=self.inventory_open,
                inventory=self.inventory,
                victory=self.victory,
                monsters_killed=self.monsters_killed,
                coins_collected=self.total_coins_collected,
            )

            pygame.display.flip()

        pygame.quit()