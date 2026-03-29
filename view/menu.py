import pygame

WIDTH, HEIGHT = 1150, 860
FPS = 60
WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
GRAY     = (110, 122, 148)
DARK_BG  = (14,  18,  34)
PANEL_BG = (22,  30,  52)
CYAN     = (0,   210, 225)
DIM_BLUE = (36,  50,  88)
PURPLE   = (160,  80, 220)


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.f_title = pygame.font.SysFont("Trebuchet MS", 50, bold=True)
        self.f_sub   = pygame.font.SysFont("Trebuchet MS", 19)
        self.f_btn   = pygame.font.SysFont("Trebuchet MS", 21, bold=True)

    @staticmethod
    def _rr(surface, color, rect, radius=12):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def _btn(self, rect, text, hovered,color_on=CYAN, color_off=DIM_BLUE, text_col=WHITE):
        
        bg = color_on if hovered else color_off
        self._rr(self.screen, bg, rect, radius=13)
        pygame.draw.rect(self.screen, color_on, rect, width=2, border_radius=13)
        surf = self.f_btn.render(text, True, BLACK if hovered else text_col)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def draw_menu(self, mx, my, click, puzzle_categories):

        self.screen.fill(DARK_BG)
        t = self.f_title.render("SUDOKU DUEL", True, CYAN)
        self.screen.blit(t, t.get_rect(centerx=WIDTH // 2, y=48))
        sub = self.f_sub.render("Backtracking  vs  Force Brute", True, GRAY)
        self.screen.blit(sub, sub.get_rect(centerx=WIDTH // 2, y=112))
        pygame.draw.line(self.screen, CYAN,(WIDTH // 2 - 200, 142), (WIDTH // 2 + 200, 142), 1)
        choose = self.f_sub.render("Choisissez une difficulte :", True, WHITE)
        self.screen.blit(choose, choose.get_rect(centerx=WIDTH // 2, y=165))

        bw, bh = 390, 56
        cx = WIDTH // 2
        result = None

        for i, (category, _files) in enumerate(puzzle_categories):
            rect = pygame.Rect(cx - bw // 2, 200 + i * (bh + 13), bw, bh)
            hov  = rect.collidepoint(mx, my)
            self._btn(rect, category, hov)
            if click and hov:
                result = category

        stats_rect = pygame.Rect(
        cx - 175, 200 + len(puzzle_categories) * (bh + 13) + 10, 350, 52)
        hov_stats = stats_rect.collidepoint(mx, my)
        self._btn(stats_rect, "STATISTIQUES", hov_stats, color_on=PURPLE, color_off=(30, 18, 50))
        if click and hov_stats:
            result = "STATS"
        return result
