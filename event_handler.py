from __future__ import annotations

from typing import TYPE_CHECKING

from map_loader import load_map_file

if TYPE_CHECKING:
    from game_panel import GamePanel


class EventHandler:
    """Owns all map-transition state and logic.

    GamePanel creates one instance and calls:
        handle_key_event(key)   — for X-key interactions (chest / door / house enter)
        update()                — per-frame tile checks (stairs, house exit gap)

    Adding a new transition in the future = add a method here and call it
    from update() or handle_key_event(). game_panel stays untouched.
    """

    def __init__(self, gp: GamePanel):
        self.gp = gp
        self._initialize_state()

    def _initialize_state(self):
        """Initialize/reset all event handler state."""
        # --- map-location flags ---
        self._in_interior = False
        self._in_cave = False

        # --- saved state for returning to outer map after house ---
        self._return_raw_rows: list[str] | None = None
        self._return_map_index: int | None = None
        self._return_spawn_tile: tuple[int, int] | None = None

        # --- persisted house object layer (door opened, chest opened, etc.) ---
        self._saved_house_objects: dict[tuple[int, int], str] | None = None

        # --- outdoor stair pending delta (applied after the frame) ---
        self._pending_map_delta = 0

        # --- stair re-trigger guard ---
        self._on_stair = False

    def reset(self):
        """Reset all event handler state (called when restarting the game)."""
        self._initialize_state()

    # ------------------------------------------------------------------
    # public queries (game_panel reads these)
    # ------------------------------------------------------------------
    @property
    def in_interior(self) -> bool:
        return self._in_interior

    @property
    def in_cave(self) -> bool:
        return self._in_cave

    # ------------------------------------------------------------------
    # key-event interactions  (called from game_panel's event loop for K_x)
    # ------------------------------------------------------------------
    def handle_key_event(self, key: int) -> bool:
        """Handle a single KEYDOWN. Returns True if the event was consumed."""
        import pygame

        if key == pygame.K_x:
            return self._handle_interact()
        return False

    def _handle_interact(self) -> bool:
        gp = self.gp

        # --- chest ---
        chest = gp._adjacent_object_tile({"c"})
        if chest is not None:
            gp.world.objects[chest] = "C"
            gp.world.rebuild_blocked()
            gp.inventory["key"] = gp.inventory.get("key", 0) + 1
            gp.sound.play_treasure()
            return True

        # --- door ---
        door = gp._adjacent_object_tile({"|"})
        if door is not None:
            if gp.inventory.get("key", 0) > 0:
                gp.inventory["key"] -= 1
                if gp.inventory["key"] <= 0:
                    gp.inventory.pop("key", None)
                gp.world.objects.pop(door, None)
                gp.world.rebuild_blocked()
                gp.sound.play_door()
            return True

        # --- house enter (only on outer map) ---
        if not self._in_interior and not self._in_cave:
            if gp._adjacent_house_tile() is not None:
                self._enter_house()
                return True

        return False

    # ------------------------------------------------------------------
    # per-frame tile checks  (called once per frame from game_panel)
    # ------------------------------------------------------------------
    def update(self):
        gp = self.gp
        tile = gp._tile_under_player()
        if tile is None:
            return

        tx, ty = tile
        t = gp.world.rows[ty][tx]
        is_stair = t in ("u", "d")

        # --- stair logic ---
        if not is_stair:
            self._on_stair = False
        elif not self._on_stair:
            self._on_stair = True
            if self._in_cave:
                if t == "u":
                    self._exit_cave_to_house()
                    return
            elif self._in_interior:
                if t == "d":
                    self._enter_cave()
                    return
            else:
                if t == "u":
                    self._pending_map_delta = 1
                elif t == "d":
                    self._pending_map_delta = -1

        # --- house exit gap: non-solid tile on the very last row ---
        if self._in_interior and ty == gp.world.h - 1 and t not in gp.tileset.solid_tiles:
            self._exit_house()
            return

    def flush_pending(self):
        """Apply any pending outdoor stair transition. Call after update()."""
        if self._pending_map_delta == 0:
            return
        delta = self._pending_map_delta
        self._pending_map_delta = 0
        gp = self.gp
        if delta > 0:
            self._load_map_by_index(gp.current_map_index + 1, spawn_on="d")
        else:
            self._load_map_by_index(gp.current_map_index - 1, spawn_on="u")

    # ------------------------------------------------------------------
    # transition methods
    # ------------------------------------------------------------------
    def _enter_house(self):
        gp = self.gp
        gp._fade("out")
        self._return_raw_rows = gp.raw_rows
        self._return_map_index = gp.current_map_index
        self._return_spawn_tile = gp._tile_under_player()
        self._in_interior = True
        self._in_cave = False

        gp.raw_rows = load_map_file(gp.map_dir / "house.txt")
        gp.reset_game(spawn_tile=(7, 7))
        # Restore persisted house object state if available.
        if self._saved_house_objects is not None:
            gp.world.objects = self._saved_house_objects
            gp.world.rebuild_blocked()
            self._saved_house_objects = None
        gp._fade("in")

    def _exit_house(self):
        gp = self.gp
        if self._return_raw_rows is None:
            return

        gp._fade("out")
        # Persist current house object state for next visit.
        self._saved_house_objects = dict(gp.world.objects)

        gp.raw_rows = self._return_raw_rows
        if self._return_map_index is not None:
            gp.current_map_index = self._return_map_index

        spawn_tile = self._return_spawn_tile
        self._return_raw_rows = None
        self._return_map_index = None
        self._return_spawn_tile = None
        self._in_interior = False
        self._in_cave = False
        gp.reset_game(spawn_tile=spawn_tile)
        gp._fade("in")

    def _enter_cave(self):
        gp = self.gp
        gp._fade("out")
        # Persist house objects before leaving for the cave.
        self._saved_house_objects = dict(gp.world.objects)
        self._in_cave = True
        self._in_interior = False
        gp.raw_rows = load_map_file(gp.map_dir / "cave.txt")
        gp.reset_game(spawn_tile=None)
        gp._fade("in")

    def _exit_cave_to_house(self):
        gp = self.gp
        gp._fade("out")
        self._in_cave = False
        self._in_interior = True
        gp.raw_rows = load_map_file(gp.map_dir / "house.txt")
        gp.reset_game(spawn_tile=(14, 6))
        # Restore persisted house object state.
        if self._saved_house_objects is not None:
            gp.world.objects = self._saved_house_objects
            gp.world.rebuild_blocked()
            self._saved_house_objects = None
        gp._fade("in")

    def _load_map_by_index(self, new_index: int, spawn_on: str | None):
        gp = self.gp
        new_index = max(0, min(new_index, len(gp.map_files) - 1))
        if new_index == gp.current_map_index:
            return

        gp._fade("out")
        gp.current_map_index = new_index
        gp.raw_rows = load_map_file(gp.map_files[gp.current_map_index])

        spawn_tile = None
        if spawn_on is not None:
            spawn_tile = gp._find_tile(spawn_on)
        gp.reset_game(spawn_tile=spawn_tile)
        gp._fade("in")