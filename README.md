# Endless Dungeons

A 2D dungeon crawler game built with Pygame.

## Features

- **Player**: Move with WASD or arrow keys, attack with Space, interact with X
- **Monsters**: Bats, Green Slimes, and Orcs that chase the player using A* pathfinding
- **Maps**: Outdoor world, house interior, and cave dungeon
- **Inventory**: Collect coins, keys, and potions; use potions with 1
- **Victory**: Find the Blue Heart in the cave to win

## Requirements

- Python 3.10+
- pygame-ce >= 2.5.0
- python-docx >= 1.1.0 (for generating the code rapport)

## Installation

```bash
pip install -r requirements.txt
```

## How to Run

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrows | Move |
| Shift | Run |
| Space | Attack |
| X | Interact (chest, door, house) |
| E | Inventory |
| 1 | Use potion |
| P | Pause |
| R | Restart (after game over / victory) |
| ESC | Quit |

## Project Structure

- `main.py` — Entry point
- `game_panel.py` — Main game loop and logic
- `player.py` — Player movement, attack, animations
- `monster.py` — Base monster class with A* pathfinding
- `world_map.py` — Map rendering and collisions
- `map_loader.py` — Load map files from `maps/`
- `asset_setter.py` — Entity placement per map
- `event_handler.py` — Map transitions (house, cave, stairs)
- `pathfinding.py` — A* algorithm
- `tileset.py` — Terrain tiles
- `object_registry.py` — Objects (doors, chests, items)
- `camera.py` — Camera follow
- `sound_manager.py` — Music and sound effects
- `ui.py` — HUD, inventory, game over, victory screens

## Generate Code Rapport

To generate the detailed code explanation as a Word document:

```bash
python generate_rapport.py
```

This creates `Rapport_Code_Endless_Dungeons.docx`.
