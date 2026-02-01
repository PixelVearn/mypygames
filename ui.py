import pygame


class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 22)

    def draw_hud(self, screen: pygame.Surface, player_hp: int, player_max_hp: int):
        hud1 = self.font.render("WASD/Arrows move | Shift run | Esc quit", True, (255, 255, 255))
        hud2 = self.font.render("E inventory | X interact/open | 1 use potion | Space attack", True, (255, 255, 255))
        screen.blit(hud1, (10, 10))
        screen.blit(hud2, (10, 32))

        hp_text = self.font.render(f"HP: {player_hp}/{player_max_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (10, 54))

    def draw_game_over(self, screen: pygame.Surface, screen_w: int, screen_h: int):
        go1 = self.font.render("GAME OVER", True, (255, 80, 80))
        go2 = self.font.render("Press R to restart", True, (255, 255, 255))
        screen.blit(go1, (screen_w // 2 - go1.get_width() // 2, screen_h // 2 - 24))
        screen.blit(go2, (screen_w // 2 - go2.get_width() // 2, screen_h // 2 + 2))

    def draw_victory(self, screen: pygame.Surface, screen_w: int, screen_h: int, monsters_killed: int, coins_collected: int):
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        title = self.font.render("VICTORY!", True, (80, 200, 255))
        subtitle = self.font.render("You found the Blue Heart!", True, (255, 255, 255))
        
        score_title = self.font.render("--- Final Score ---", True, (220, 220, 220))
        monsters_text = self.font.render(f"Monsters Defeated: {monsters_killed}", True, (255, 200, 100))
        coins_text = self.font.render(f"Coins Collected: {coins_collected}", True, (255, 215, 0))
        
        restart = self.font.render("Press R to play again", True, (200, 200, 200))
        
        y_start = screen_h // 2 - 80
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, y_start))
        screen.blit(subtitle, (screen_w // 2 - subtitle.get_width() // 2, y_start + 30))
        screen.blit(score_title, (screen_w // 2 - score_title.get_width() // 2, y_start + 70))
        screen.blit(monsters_text, (screen_w // 2 - monsters_text.get_width() // 2, y_start + 100))
        screen.blit(coins_text, (screen_w // 2 - coins_text.get_width() // 2, y_start + 125))
        screen.blit(restart, (screen_w // 2 - restart.get_width() // 2, y_start + 165))

    def draw_paused(self, screen: pygame.Surface, screen_w: int, screen_h: int):
        p1 = self.font.render("PAUSED", True, (255, 255, 255))
        p2 = self.font.render("Press P to resume", True, (255, 255, 255))
        screen.blit(p1, (screen_w // 2 - p1.get_width() // 2, screen_h // 2 - 24))
        screen.blit(p2, (screen_w // 2 - p2.get_width() // 2, screen_h // 2 + 2))

    def draw_inventory(self, screen: pygame.Surface, screen_w: int, screen_h: int, inventory: dict[str, int]):
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        title = self.font.render("INVENTORY (E to close)", True, (255, 255, 255))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 60))

        if not inventory:
            empty = self.font.render("(empty)", True, (220, 220, 220))
            screen.blit(empty, (screen_w // 2 - empty.get_width() // 2, 92))
            return

        y = 92
        for name, count in inventory.items():
            line = self.font.render(f"{name}: {count}", True, (220, 220, 220))
            screen.blit(line, (screen_w // 2 - line.get_width() // 2, y))
            y += 22

    def draw(
        self,
        screen: pygame.Surface,
        screen_w: int,
        screen_h: int,
        player_hp: int,
        player_max_hp: int,
        paused: bool,
        game_over: bool,
        inventory_open: bool,
        inventory: dict[str, int],
        victory: bool = False,
        monsters_killed: int = 0,
        coins_collected: int = 0,
    ):
        self.draw_hud(screen, player_hp, player_max_hp)
        if victory:
            self.draw_victory(screen, screen_w, screen_h, monsters_killed, coins_collected)
        elif game_over:
            self.draw_game_over(screen, screen_w, screen_h)
        if paused:
            self.draw_paused(screen, screen_w, screen_h)
        if inventory_open:
            self.draw_inventory(screen, screen_w, screen_h, inventory)