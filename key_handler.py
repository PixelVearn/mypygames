"""
Key Handler Module

Centralizes all keyboard input logic for the game.
Organizes key bindings into logical categories and provides clean separation of concerns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game_panel import GamePanel


class KeyAction:
    """Enum-like class for key actions to avoid magic strings."""
    
    # System controls
    QUIT = "quit"
    PAUSE = "pause"
    RESTART = "restart"
    
    # Inventory controls
    TOGGLE_INVENTORY = "toggle_inventory"
    USE_POTION = "use_potion"
    
    # Player actions
    ATTACK = "attack"
    INTERACT = "interact"
    
    # Movement (handled separately in player.py)
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    RUN = "run"


class KeyBindings:
    """
    Defines all key bindings for the game.
    Modify these mappings to change controls.
    """
    
    def __init__(self):
        # System controls
        self.quit_keys = {pygame.K_ESCAPE}
        self.pause_keys = {pygame.K_p}
        self.restart_keys = {pygame.K_r}
        
        # Inventory controls
        self.inventory_toggle_keys = {pygame.K_e}
        self.use_potion_keys = {pygame.K_1}
        
        # Player actions
        self.attack_keys = {pygame.K_SPACE}
        self.interact_keys = {pygame.K_x}
        
        # Movement keys (for reference, actual handling in player.py)
        self.move_up_keys = {pygame.K_w, pygame.K_UP}
        self.move_down_keys = {pygame.K_s, pygame.K_DOWN}
        self.move_left_keys = {pygame.K_a, pygame.K_LEFT}
        self.move_right_keys = {pygame.K_d, pygame.K_RIGHT}
        self.run_keys = {pygame.K_LSHIFT, pygame.K_RSHIFT}
    
    def get_action_for_key(self, key: int) -> str | None:
        """
        Map a pygame key to a KeyAction.
        Returns None if the key is not bound to any action.
        """
        if key in self.quit_keys:
            return KeyAction.QUIT
        if key in self.pause_keys:
            return KeyAction.PAUSE
        if key in self.restart_keys:
            return KeyAction.RESTART
        if key in self.inventory_toggle_keys:
            return KeyAction.TOGGLE_INVENTORY
        if key in self.use_potion_keys:
            return KeyAction.USE_POTION
        if key in self.attack_keys:
            return KeyAction.ATTACK
        if key in self.interact_keys:
            return KeyAction.INTERACT
        
        return None


class KeyHandler:
    """
    Central keyboard input handler for the game.
    
    Responsibilities:
    - Process pygame KEYDOWN events
    - Route actions to appropriate handlers based on game state
    - Maintain clean separation between input detection and action execution
    """
    
    def __init__(self, game_panel: GamePanel):
        self.gp = game_panel
        self.bindings = KeyBindings()
    
    # ------------------------------------------------------------------
    # Main event processing
    # ------------------------------------------------------------------
    
    def handle_keydown(self, key: int) -> bool:
        """
        Process a KEYDOWN event.
        
        Args:
            key: pygame key constant (e.g., pygame.K_SPACE)
        
        Returns:
            True if the game should quit, False otherwise
        """
        action = self.bindings.get_action_for_key(key)
        
        if action is None:
            return False
        
        # Route to appropriate handler based on action type
        if action == KeyAction.QUIT:
            return self._handle_quit()
        elif action == KeyAction.PAUSE:
            self._handle_pause()
        elif action == KeyAction.RESTART:
            self._handle_restart()
        elif action == KeyAction.TOGGLE_INVENTORY:
            self._handle_inventory_toggle()
        elif action == KeyAction.USE_POTION:
            self._handle_use_potion()
        elif action == KeyAction.ATTACK:
            self._handle_attack()
        elif action == KeyAction.INTERACT:
            self._handle_interact()
        
        return False
    
    # ------------------------------------------------------------------
    # System control handlers
    # ------------------------------------------------------------------
    
    def _handle_quit(self) -> bool:
        """Handle quit action (ESC key)."""
        return True
    
    def _handle_pause(self) -> None:
        """Handle pause toggle (P key)."""
        if not self.gp.game_over:
            self.gp.paused = not self.gp.paused
    
    def _handle_restart(self) -> None:
        """Handle restart after game over (R key)."""
        if not self.gp.game_over:
            return
        
        # Import here to avoid circular dependency
        from map_loader import load_map_file
        
        # Reset all game statistics
        self.gp.monsters_killed = 0
        self.gp.total_coins_collected = 0
        self.gp.inventory.clear()
        
        # Reset event handler state (clears map transition state)
        self.gp.events.reset()
        
        # Return to main map
        self.gp.current_map_index = 0
        self.gp.raw_rows = load_map_file(self.gp.map_files[self.gp.current_map_index])
        
        # Reset the game world
        self.gp.reset_game()
    
    # ------------------------------------------------------------------
    # Inventory control handlers
    # ------------------------------------------------------------------
    
    def _handle_inventory_toggle(self) -> None:
        """Handle inventory toggle (E key)."""
        if self.gp.inventory_open:
            # Close inventory
            self.gp.inventory_open = False
        elif not self.gp.game_over and not self.gp.paused:
            # Open inventory (only if game is active)
            self.gp.inventory_open = True
    
    def _handle_use_potion(self) -> None:
        """Handle potion use (1 key)."""
        # Can only use potion during active gameplay
        if self.gp.game_over or self.gp.paused:
            return
        
        # Check if player has potions and is alive
        if self.gp.inventory.get("potion", 0) <= 0:
            return
        
        if self.gp.player.hp <= 0:
            return
        
        # Use potion
        self.gp.inventory["potion"] -= 1
        if self.gp.inventory["potion"] <= 0:
            self.gp.inventory.pop("potion", None)
        
        # Heal player (max 2 HP per potion)
        self.gp.player.hp = min(self.gp.player.max_hp, self.gp.player.hp + 2)
    
    # ------------------------------------------------------------------
    # Player action handlers
    # ------------------------------------------------------------------
    
    def _handle_attack(self) -> None:
        """Handle player attack (SPACE key)."""
        # Can only attack during active gameplay (not in inventory, not paused, not game over)
        if self.gp.game_over or self.gp.paused or self.gp.inventory_open:
            return
        
        # Try to start attack animation
        if self.gp.player.start_attack():
            self.gp.sound.play_swing()
    
    def _handle_interact(self) -> None:
        """Handle player interact (X key)."""
        # Can only interact during active gameplay
        if self.gp.game_over or self.gp.paused or self.gp.inventory_open:
            return
        
        # Delegate to event handler for chest/door/house interactions
        self.gp.events.handle_key_event(pygame.K_x)
    
    # ------------------------------------------------------------------
    # Query methods for other modules
    # ------------------------------------------------------------------
    
    def get_control_hints(self) -> dict[str, str]:
        """
        Get human-readable control hints for UI display.
        
        Returns:
            Dictionary mapping action categories to control hint strings
        """
        return {
            "movement": "WASD/Arrows move | Shift run",
            "actions": "Space attack | X interact",
            "inventory": "E inventory | 1 use potion",
            "system": "P pause | R restart | Esc quit",
        }
    
    def is_movement_key(self, key: int) -> bool:
        """Check if a key is used for movement."""
        return (
            key in self.bindings.move_up_keys
            or key in self.bindings.move_down_keys
            or key in self.bindings.move_left_keys
            or key in self.bindings.move_right_keys
        )
    
    def is_run_key(self, key: int) -> bool:
        """Check if a key is used for running."""
        return key in self.bindings.run_keys


class InputState:
    """
    Optional: Track the current state of all inputs for query-based input handling.
    This is useful for continuous actions (like movement) vs discrete actions (like attack).
    
    Currently movement is handled in player.py using pygame.key.get_pressed(),
    but this class provides an alternative approach if needed.
    """
    
    def __init__(self):
        self.pressed_keys: set[int] = set()
    
    def update(self):
        """Update input state from pygame."""
        keys = pygame.key.get_pressed()
        self.pressed_keys.clear()
        for i in range(len(keys)):
            if keys[i]:
                self.pressed_keys.add(i)
    
    def is_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return key in self.pressed_keys
    
    def any_pressed(self, keys: set[int]) -> bool:
        """Check if any key in a set is pressed."""
        return bool(self.pressed_keys & keys)