from pathlib import Path

from game_panel import GamePanel


PROJECT_DIR = Path(__file__).resolve().parent


def main():
    GamePanel(PROJECT_DIR).run()


if __name__ == "__main__":
    main()