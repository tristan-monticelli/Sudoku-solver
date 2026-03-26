"""
visuel.py
---------
Classe Renderer — rendu Pygame pour Sudoku Duel.
Aucune logique de jeu : reçoit des données, dessine, retourne des actions.
"""

import pygame

# ─────────────────────────────────────────────────────────────────────────────
#  Constantes UI
# ─────────────────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1150, 860
FPS = 60

WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
GRAY     = (110, 122, 148)
GREEN    = (46,  204, 113)
RED      = (231, 76,  60)
DARK_BG  = (14,  18,  34)
PANEL_BG = (22,  30,  52)
PANEL2   = (18,  24,  44)
GOLD     = (241, 196,  15)
SILVER   = (160, 172, 185)
CYAN     = (0,   210, 225)
ORANGE   = (255, 138,  45)
DIM_BLUE = (36,  50,  88)
PURPLE   = (160,  80, 220)
LINE_COL = (40,  58,  98)

CELL    = 44
GRID_PX = CELL * 9


# ─────────────────────────────────────────────────────────────────────────────
#  Renderer
# ─────────────────────────────────────────────────────────────────────────────
class Renderer:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku Duel : Backtracking vs Force Brute")
        self.clock = pygame.time.Clock()

        self.f_title  = pygame.font.SysFont("Trebuchet MS", 50, bold=True)
        self.f_sub    = pygame.font.SysFont("Trebuchet MS", 19)
        self.f_btn    = pygame.font.SysFont("Trebuchet MS", 21, bold=True)
        self.f_grid   = pygame.font.SysFont("Consolas",     22, bold=True)
        self.f_timer  = pygame.font.SysFont("Consolas",     34, bold=True)
        self.f_big    = pygame.font.SysFont("Trebuchet MS", 88, bold=True)
        self.f_podium = pygame.font.SysFont("Trebuchet MS", 23, bold=True)
        self.f_small  = pygame.font.SysFont("Consolas",     14)
        self.f_label  = pygame.font.SysFont("Trebuchet MS", 16, bold=True)
        self.f_stat   = pygame.font.SysFont("Consolas",     16)
        self.f_stat_h = pygame.font.SysFont("Trebuchet MS", 18, bold=True)

    # ── Utilitaires ─────────────────────────────────────────────────────────

    def tick(self):
        self.clock.tick(FPS)

    def flip(self):
        pygame.display.flip()

    def quit(self):
        pygame.quit()

    def poll_events(self) -> tuple[int, int, bool, bool]:
        """Retourne (mouse_x, mouse_y, click, should_quit)."""
        mx, my = pygame.mouse.get_pos()
        click = False
        should_quit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                should_quit = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
        return mx, my, click, should_quit

    @staticmethod
    def _fmt(t: float) -> str:
        if t <= 0:   return "—"
        if t >= 60:  return f"{t/60:.1f} min"
        if t >= 1:   return f"{t:.3f} s"
        return f"{t*1000:.2f} ms"

    # ── Helpers de dessin ───────────────────────────────────────────────────

    @staticmethod
    def _rr(surface, color, rect, radius=12):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def _btn(self, rect, text, hovered,
             color_on=CYAN, color_off=DIM_BLUE, text_col=WHITE):
        bg = color_on if hovered else color_off
        self._rr(self.screen, bg, rect, radius=13)
        pygame.draw.rect(self.screen, color_on, rect, width=2, border_radius=13)
        surf = self.f_btn.render(text, True, BLACK if hovered else text_col)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_grid(self, x, y, grid, initial_mask, label, label_color, done):
        panel = pygame.Rect(x - 6, y - 6, GRID_PX + 12, GRID_PX + 12)
        self._rr(self.screen, PANEL_BG, panel, radius=8)
        for r in range(9):
            for c in range(9):
                cx = x + c * CELL
                cy = y + r * CELL
                cr = pygame.Rect(cx, cy, CELL, CELL)
                bg = (28, 38, 62) if (r//3 + c//3) % 2 == 0 else (20, 28, 48)
                pygame.draw.rect(self.screen, bg, cr)
                val = grid[r][c]
                if val:
                    col = WHITE if initial_mask[r][c] else label_color
                    t = self.f_grid.render(str(val), True, col)
                    self.screen.blit(t, t.get_rect(center=cr.center))
        for i in range(10):
            w   = 3 if i % 3 == 0 else 1
            col = label_color if i % 3 == 0 else LINE_COL
            pygame.draw.line(self.screen, col,
                             (x, y + i*CELL), (x + GRID_PX, y + i*CELL), w)
            pygame.draw.line(self.screen, col,
                             (x + i*CELL, y), (x + i*CELL, y + GRID_PX), w)
        lbl = self.f_label.render(label, True, label_color)
        self.screen.blit(lbl, lbl.get_rect(centerx=x + GRID_PX//2, y=y - 28))
        st_txt = "Termine !" if done else "En cours..."
        st     = self.f_small.render(st_txt, True, GREEN if done else GRAY)
        self.screen.blit(st, st.get_rect(centerx=x + GRID_PX//2, y=y + GRID_PX + 7))

    def _draw_timer_panel(self, cx, cy, timer_val):
        panel = pygame.Rect(cx - 72, cy - 58, 144, 116)
        self._rr(self.screen, PANEL_BG, panel, radius=14)
        pygame.draw.rect(self.screen, GOLD, panel, width=2, border_radius=14)
        lbl = self.f_small.render("CHRONO", True, GRAY)
        self.screen.blit(lbl, lbl.get_rect(centerx=cx, y=cy - 43))
        t = self.f_timer.render(f"{timer_val:.2f}s", True, GOLD)
        self.screen.blit(t, t.get_rect(center=(cx, cy)))

    # ─────────────────────────────────────────────────────────────────────────
    #  Ecran MENU
    # ─────────────────────────────────────────────────────────────────────────

    def draw_menu(self, mx, my, click, puzzle_categories):
        """Retourne le nom de catégorie si cliqué, 'STATS' si stats, None sinon."""
        self.screen.fill(DARK_BG)

        t = self.f_title.render("SUDOKU DUEL", True, CYAN)
        self.screen.blit(t, t.get_rect(centerx=WIDTH//2, y=48))

        sub = self.f_sub.render("Backtracking  vs  Force Brute", True, GRAY)
        self.screen.blit(sub, sub.get_rect(centerx=WIDTH//2, y=112))
        pygame.draw.line(self.screen, CYAN,
                         (WIDTH//2 - 200, 142), (WIDTH//2 + 200, 142), 1)

        choose = self.f_sub.render("Choisissez une difficulte :", True, WHITE)
        self.screen.blit(choose, choose.get_rect(centerx=WIDTH//2, y=165))

        bw, bh = 390, 56
        cx = WIDTH // 2
        result = None

        for i, (category, _files) in enumerate(puzzle_categories):
            rect = pygame.Rect(cx - bw//2, 200 + i*(bh + 13), bw, bh)
            hov  = rect.collidepoint(mx, my)
            self._btn(rect, category, hov)
            if click and hov:
                result = category

        stats_rect = pygame.Rect(cx - 175, 200 + len(puzzle_categories)*(bh+13) + 10, 350, 52)
        hov_stats  = stats_rect.collidepoint(mx, my)
        self._btn(stats_rect, "STATISTIQUES", hov_stats,
                  color_on=PURPLE, color_off=(30, 18, 50))
        if click and hov_stats:
            result = "STATS"

        return result

    # ─────────────────────────────────────────────────────────────────────────
    #  Ecran COUNTDOWN
    # ─────────────────────────────────────────────────────────────────────────

    def draw_countdown(self, grid_bt, grid_bf, initial_mask, current_label, elapsed):
        """Retourne True quand le décompte est terminé."""
        self.screen.fill(DARK_BG)

        grid_y  = 68
        left_x  = 35
        right_x = WIDTH - 35 - GRID_PX
        self._draw_grid(left_x,  grid_y, grid_bt, initial_mask, "BACKTRACKING", CYAN,   False)
        self._draw_grid(right_x, grid_y, grid_bf, initial_mask, "BRUTE FORCE",  ORANGE, False)

        overlay_w, overlay_h = 340, 210
        cx, cy = WIDTH // 2, HEIGHT // 2
        overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
        overlay.fill((10, 14, 28, 215))
        pygame.draw.rect(overlay, (0, 210, 225, 90),
                         overlay.get_rect(), width=2, border_radius=18)
        self.screen.blit(overlay, (cx - overlay_w // 2, cy - overlay_h // 2))

        val = 3 - int(elapsed)
        if val > 0:
            hint = self.f_sub.render(f"Puzzle : {current_label}", True, GRAY)
            self.screen.blit(hint, hint.get_rect(centerx=cx, y=cy - 82))
            ready = self.f_sub.render("Prêt ?", True, WHITE)
            self.screen.blit(ready, ready.get_rect(centerx=cx, y=cy - 54))
            n = self.f_big.render(str(val), True, RED)
            self.screen.blit(n, n.get_rect(center=(cx, cy + 22)))
            return False
        return True

    # ─────────────────────────────────────────────────────────────────────────
    #  Ecran DUEL
    # ─────────────────────────────────────────────────────────────────────────

    def draw_duel(self, grid_bt, grid_bf, initial_mask,
                  current_label, timer_val, finish_bt, finish_bf):
        self.screen.fill(DARK_BG)
        title = self.f_sub.render(
            f"Resolution en cours  |  {current_label}", True, GRAY)
        self.screen.blit(title, title.get_rect(centerx=WIDTH//2, y=14))

        grid_y  = 68
        left_x  = 35
        right_x = WIDTH - 35 - GRID_PX

        self._draw_grid(left_x,  grid_y, grid_bt, initial_mask, "BACKTRACKING", CYAN,   finish_bt)
        self._draw_grid(right_x, grid_y, grid_bf, initial_mask, "BRUTE FORCE",  ORANGE, finish_bf)
        self._draw_timer_panel(WIDTH//2, grid_y + GRID_PX//2, timer_val)

    # ─────────────────────────────────────────────────────────────────────────
    #  Ecran RESULTS
    # ─────────────────────────────────────────────────────────────────────────

    def draw_results(self, mx, my, click, current_label,
                     time_bt, time_bf, timer_val, history_data):
        """Retourne 'REPLAY', 'STATS', 'MENU' ou None."""
        self.screen.fill(BLACK)
        cx = WIDTH // 2

        t = self.f_title.render("CLASSEMENT", True, WHITE)
        self.screen.blit(t, t.get_rect(centerx=cx, y=32))

        plbl = self.f_sub.render(current_label, True, GRAY)
        self.screen.blit(plbl, plbl.get_rect(centerx=cx, y=96))

        results = sorted(
            [("Backtracking", time_bt, CYAN),
             ("Brute Force",  time_bf, ORANGE)],
            key=lambda x: x[1]
        )
        winner, loser = results[0], results[1]

        p1 = pygame.Rect(cx - 285, 140, 245, 178)
        self._rr(self.screen, (32, 28, 0), p1, 12)
        pygame.draw.rect(self.screen, GOLD, p1, width=3, border_radius=12)
        for surf, yoff in [
            (self.f_podium.render("1er", True, GOLD), 14),
            (self.f_podium.render(winner[0], True, winner[2]), 54),
            (self.f_timer.render(self._fmt(winner[1]), True, WHITE), 96),
            (self.f_small.render("O(9^n) + MRV", True, GRAY), 148),
        ]:
            self.screen.blit(surf, surf.get_rect(centerx=p1.centerx, y=p1.y+yoff))

        runs_bt = len(history_data.get("bt", []))
        r_txt = self.f_small.render(f"({runs_bt} run(s) ce niveau)", True, GRAY)
        self.screen.blit(r_txt, r_txt.get_rect(centerx=p1.centerx, y=p1.y+165))

        p2 = pygame.Rect(cx + 40, 170, 245, 148)
        self._rr(self.screen, (18, 18, 18), p2, 12)
        pygame.draw.rect(self.screen, SILVER, p2, width=2, border_radius=12)
        for surf, yoff in [
            (self.f_podium.render("2e", True, SILVER), 14),
            (self.f_podium.render(loser[0], True, loser[2]), 50),
            (self.f_podium.render(self._fmt(loser[1]), True, WHITE), 88),
            (self.f_small.render("O(9^n) ordre fixe", True, GRAY), 120),
        ]:
            self.screen.blit(surf, surf.get_rect(centerx=p2.centerx, y=p2.y+yoff))

        if winner[1] > 0 and loser[1] > 0:
            ratio = loser[1] / winner[1]
            sp = self.f_sub.render(
                f"{winner[0]} : {ratio:.1f}x plus rapide sur ce puzzle", True, GOLD)
            self.screen.blit(sp, sp.get_rect(centerx=cx, y=345))

        hx = [cx - 320, cx - 65, cx + 148]
        y0 = 382
        pygame.draw.line(self.screen, LINE_COL, (cx-330, y0-4), (cx+270, y0-4))
        for i, h in enumerate(["Algorithme", "Complexite", "Temps"]):
            self.screen.blit(self.f_small.render(h, True, CYAN), (hx[i], y0))
        y0 += 20
        pygame.draw.line(self.screen, LINE_COL, (cx-330, y0-4), (cx+270, y0-4))
        for name, tv, _ in results:
            cplx = "O(9^n) + MRV" if name == "Backtracking" else "O(9^n) ordre fixe"
            for i, val in enumerate([name, cplx, self._fmt(tv)]):
                self.screen.blit(self.f_small.render(val, True, WHITE), (hx[i], y0))
            y0 += 20
        pygame.draw.line(self.screen, LINE_COL, (cx-330, y0), (cx+270, y0))

        y0 += 16
        bt_runs = history_data.get("bt", [])
        bf_runs = history_data.get("bf", [])
        if bt_runs:
            avg_bt = sum(bt_runs) / len(bt_runs)
            avg_bf = sum(bf_runs) / len(bf_runs) if bf_runs else 0
            preview = self.f_small.render(
                f"Moy. ce niveau — BT : {self._fmt(avg_bt)}   |   BF : {self._fmt(avg_bf)}   ({len(bt_runs)} run(s))",
                True, PURPLE)
            self.screen.blit(preview, preview.get_rect(centerx=cx, y=y0))

        bw, bh  = 190, 50
        btn_y   = HEIGHT - 88
        btn_replay = pygame.Rect(cx - 305, btn_y, bw, bh)
        btn_stats  = pygame.Rect(cx - 95,  btn_y, bw, bh)
        btn_menu   = pygame.Rect(cx + 115, btn_y, bw, bh)

        self._btn(btn_replay, "Rejouer", btn_replay.collidepoint(mx, my), ORANGE, (40,18,0))
        self._btn(btn_stats,  "Stats",   btn_stats.collidepoint(mx, my),  PURPLE, (28,14,48))
        self._btn(btn_menu,   "Menu",    btn_menu.collidepoint(mx, my),   CYAN,   DIM_BLUE)

        if click:
            if btn_replay.collidepoint(mx, my):
                return "REPLAY"
            elif btn_stats.collidepoint(mx, my):
                return "STATS"
            elif btn_menu.collidepoint(mx, my):
                return "MENU"
        return None

    # ─────────────────────────────────────────────────────────────────────────
    #  Ecran STATS
    # ─────────────────────────────────────────────────────────────────────────

    def draw_stats(self, mx, my, click, puzzle_categories, history):
        """Retourne True si le bouton Retour est cliqué."""
        self.screen.fill(DARK_BG)
        cx = WIDTH // 2

        # ── Titre ─────────────────────────────────────────────────────────
        t = self.f_title.render("STATISTIQUES", True, PURPLE)
        self.screen.blit(t, t.get_rect(centerx=cx, y=22))

        sub = self.f_sub.render("Temps moyen par niveau  —  session en cours", True, GRAY)
        self.screen.blit(sub, sub.get_rect(centerx=cx, y=82))
        pygame.draw.line(self.screen, PURPLE, (cx-250, 108), (cx+250, 108), 1)

        # ── Tableau compact ───────────────────────────────────────────────
        col_x = [cx - 390, cx - 120, cx + 50, cx + 220]
        col_h = ["Niveau", "Moy. Backtracking", "Moy. Brute Force", "Runs"]

        y0 = 122
        self._rr(self.screen, PANEL2,
                 pygame.Rect(cx - 410, y0 - 4, 820, 24), radius=6)
        for i, h in enumerate(col_h):
            self.screen.blit(self.f_stat_h.render(h, True, CYAN), (col_x[i], y0))
        y0 += 28

        all_bt: list[float] = []
        all_bf: list[float] = []
        avgs_bt: list[float | None] = []
        avgs_bf: list[float | None] = []
        short_labels: list[str]     = []

        for idx, (cat, _files) in enumerate(puzzle_categories):
            data   = history.get(cat, {"bt": [], "bf": []})
            bt_lst = data["bt"]
            bf_lst = data["bf"]
            runs   = len(bt_lst)

            avg_bt = sum(bt_lst) / runs        if runs    else None
            avg_bf = sum(bf_lst) / len(bf_lst) if bf_lst  else None

            avgs_bt.append(avg_bt)
            avgs_bf.append(avg_bf)
            short_labels.append(cat[:3])

            all_bt += bt_lst
            all_bf += bf_lst

            row_bg = (22, 30, 52) if idx % 2 == 0 else (18, 24, 42)
            self._rr(self.screen, row_bg,
                     pygame.Rect(cx - 410, y0 - 2, 820, 22), radius=4)

            self.screen.blit(
                self.f_stat.render(cat, True, WHITE),
                (col_x[0], y0))
            self.screen.blit(
                self.f_stat.render(self._fmt(avg_bt) if avg_bt else "—",
                                   True, CYAN   if avg_bt else GRAY),
                (col_x[1], y0))
            self.screen.blit(
                self.f_stat.render(self._fmt(avg_bf) if avg_bf else "—",
                                   True, ORANGE if avg_bf else GRAY),
                (col_x[2], y0))
            self.screen.blit(
                self.f_stat.render(str(runs) if runs else "0",
                                   True, GREEN if runs else GRAY),
                (col_x[3], y0))
            y0 += 24

        # ── Diagramme en barres groupées ──────────────────────────────────
        chart_margin_top = 18
        chart_left   = cx - 390
        chart_w      = 820
        chart_h      = 195
        chart_top    = y0 + chart_margin_top
        chart_bottom = chart_top + chart_h

        self._rr(self.screen, PANEL_BG,
                 pygame.Rect(chart_left - 8, chart_top - 20, chart_w + 16, chart_h + 50),
                 radius=10)

        ct = self.f_stat_h.render("Diagramme en barres — Temps moyen (ms / s)", True, PURPLE)
        self.screen.blit(ct, ct.get_rect(centerx=cx, y=chart_top - 16))

        all_vals = [v for v in avgs_bt + avgs_bf if v is not None]
        max_val  = max(all_vals) if all_vals else 1.0

        n        = len(puzzle_categories)
        group_w  = chart_w // n
        bar_w    = max(14, group_w // 3)
        gap      = 6

        for idx in range(n):
            group_cx = chart_left + idx * group_w + group_w // 2
            bx_bt    = group_cx - bar_w - gap // 2
            bx_bf    = group_cx + gap // 2

            for bx, avg, color in [
                (bx_bt, avgs_bt[idx], CYAN),
                (bx_bf, avgs_bf[idx], ORANGE),
            ]:
                if avg is not None and max_val > 0:
                    bar_h = max(4, int((avg / max_val) * (chart_h - 28)))
                    bar_rect = pygame.Rect(bx, chart_bottom - bar_h, bar_w, bar_h)
                    self._rr(self.screen, color, bar_rect, radius=4)
                    hl = pygame.Surface((bar_w, min(5, bar_h)), pygame.SRCALPHA)
                    hl.fill((*WHITE, 55))
                    self.screen.blit(hl, (bx, chart_bottom - bar_h))
                    vt = self.f_small.render(self._fmt(avg), True, color)
                    self.screen.blit(vt, vt.get_rect(
                        centerx=bx + bar_w // 2,
                        bottom=chart_bottom - bar_h - 2))
                else:
                    pygame.draw.rect(self.screen, (40, 50, 80),
                                     pygame.Rect(bx, chart_bottom - 5, bar_w, 5),
                                     border_radius=2)

            ls = self.f_small.render(short_labels[idx], True, GRAY)
            self.screen.blit(ls, ls.get_rect(centerx=group_cx, y=chart_bottom + 5))

        pygame.draw.line(self.screen, GRAY,
                         (chart_left - 2, chart_bottom),
                         (chart_left + chart_w + 2, chart_bottom), 1)

        leg_y = chart_bottom + 22
        for color, txt in [(CYAN, "■  Backtracking"), (ORANGE, "■  Brute Force")]:
            s = self.f_small.render(txt, True, color)
            offset = -100 if color == CYAN else 100
            self.screen.blit(s, s.get_rect(centerx=cx + offset, y=leg_y))

        # ── Résumé global ─────────────────────────────────────────────────
        glob_bt    = sum(all_bt) / len(all_bt) if all_bt else None
        glob_bf    = sum(all_bf) / len(all_bf) if all_bf else None
        total_runs = len(all_bt)

        y_glob  = chart_bottom + 42
        panel_g = pygame.Rect(cx - 410, y_glob, 820, 56)
        self._rr(self.screen, PANEL2, panel_g, radius=8)
        pygame.draw.rect(self.screen, PURPLE, panel_g, width=1, border_radius=8)

        self.screen.blit(
            self.f_stat_h.render("Moy. globale :", True, PURPLE),
            (cx - 390, y_glob + 8))
        self.screen.blit(
            self.f_stat.render(f"BT : {self._fmt(glob_bt) if glob_bt else '—'}", True, CYAN),
            (cx - 220, y_glob + 10))
        self.screen.blit(
            self.f_stat.render(f"BF : {self._fmt(glob_bf) if glob_bf else '—'}", True, ORANGE),
            (cx + 20, y_glob + 10))
        self.screen.blit(
            self.f_stat.render(f"{total_runs} run(s)", True, GRAY),
            (cx + 260, y_glob + 10))

        if glob_bt and glob_bf and glob_bt > 0:
            sp   = glob_bf / glob_bt
            sp_s = self.f_small.render(
                f"BT {sp:.1f}x plus rapide en moyenne globale", True, GOLD)
            self.screen.blit(sp_s, sp_s.get_rect(centerx=cx, y=y_glob + 34))

        # ── Bouton retour ─────────────────────────────────────────────────
        btn_back = pygame.Rect(cx - 100, HEIGHT - 54, 200, 44)
        self._btn(btn_back, "Retour",
                  btn_back.collidepoint(mx, my), PURPLE, (28, 14, 48))
        if click and btn_back.collidepoint(mx, my):
            return True
        return False
