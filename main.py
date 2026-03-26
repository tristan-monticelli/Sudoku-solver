"""
main.py
-------
GameController — logique de jeu, threads solveurs, affichage terminal.
Point d'entrée : python main.py
"""

import time
import threading
import copy
import sys
import os

from grid import SudokuGrid
from visuel import Renderer

# ── Codes ANSI terminal ───────────────────────────────────────────────────────
_R  = "\033[0m"
_B  = "\033[1m"
_CY = "\033[96m"
_YL = "\033[93m"
_GR = "\033[92m"
_GY = "\033[90m"
_MG = "\033[95m"
_WH = "\033[97m"

# ── Config ────────────────────────────────────────────────────────────────────
PUZZLE_FILES = [
    ("SUDOKU 1  —  Facile",      "sudoku.txt"),
    ("SUDOKU 2  —  Moyen",       "sudoku2.txt"),
    ("SUDOKU 3  —  Difficile",   "sudoku3.txt"),
    ("SUDOKU 4  —  Difficile+",  "sudoku4.txt"),
    ("SUDOKU 5  —  Evil",        "evilsudoku.txt"),
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

_VISUAL_THROTTLE = 500


# ─────────────────────────────────────────────────────────────────────────────
#  Affichage terminal
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_time(t: float) -> str:
    if t <= 0:   return "—"
    if t >= 60:  return f"{t/60:.1f} min"
    if t >= 1:   return f"{t:.3f} s"
    return f"{t*1000:.2f} ms"


def _print_duel_terminal(label: str,
                          grid_bt: list[list[int]],
                          grid_bf: list[list[int]],
                          initial_mask: list[list[bool]],
                          time_bt: float,
                          time_bf: float) -> None:
    """Affiche les deux grilles résolues côte à côte dans le terminal."""
    import re

    def strip_ansi(s):
        return re.sub(r'\033\[[0-9;]*m', '', s)

    def pad_to(s, width):
        return s + " " * max(0, width - len(strip_ansi(s)))

    def build_grid_lines(grid, mask, color):
        TOP = f"  {_GY}┌───────┬───────┬───────┐{_R}"
        BOT = f"  {_GY}└───────┴───────┴───────┘{_R}"
        MID = f"  {_GY}├───────┼───────┼───────┤{_R}"
        lines = [TOP]
        for r in range(9):
            if r in (3, 6):
                lines.append(MID)
            s = f"  {_GY}│{_R}"
            for c in range(9):
                if c in (3, 6):
                    s += f"{_GY}│{_R}"
                val = grid[r][c]
                if val == 0:
                    s += f" {_GY}·{_R} "
                elif mask[r][c]:
                    s += f" {_B}{val}{_R} "
                else:
                    s += f" {color}{val}{_R} "
            s += f"{_GY}│{_R}"
            lines.append(s)
        lines.append(BOT)
        return lines

    PAD = 38

    bt_lines = build_grid_lines(grid_bt, initial_mask, _CY)
    bf_lines = build_grid_lines(grid_bf, initial_mask, _YL)

    print(f"\n{_B}{_MG}{'═' * 74}{_R}")
    print(f"{_B}{_MG}  SUDOKU DUEL  —  {label}{_R}")
    print(f"{_B}{_MG}{'═' * 74}{_R}\n")

    print(pad_to(f"  {_CY}{_B}BACKTRACKING{_R}", PAD + 14) +
          f"     {_YL}{_B}BRUTE FORCE{_R}")
    print(f"  {_GY}{'─' * (PAD - 2)}{_R}     {_GY}{'─' * (PAD - 2)}{_R}")

    for bt_l, bf_l in zip(bt_lines, bf_lines):
        print(pad_to(bt_l, PAD + 14) + "     " + bf_l)

    bt_faster = (time_bt <= time_bf)
    print()
    print(pad_to(
        f"  {_CY}Temps :{_R} {_B}{_fmt_time(time_bt)}{_R}"
        + (f"  {_GR}★ WINNER{_R}" if bt_faster else ""),
        PAD + 14
    ) + f"     {_YL}Temps :{_R} {_B}{_fmt_time(time_bf)}{_R}"
        + (f"  {_GR}★ WINNER{_R}" if not bt_faster else ""))

    if time_bt > 0 and time_bf > 0:
        ratio  = max(time_bt, time_bf) / min(time_bt, time_bf)
        faster = "Backtracking" if bt_faster else "Brute Force"
        print(f"\n  {_B}{faster}{_R} est {_GR}{ratio:.1f}x plus rapide{_R} sur ce puzzle.")

    print(f"\n{_GY}{'─' * 74}{_R}\n")


# ─────────────────────────────────────────────────────────────────────────────
#  GameController
# ─────────────────────────────────────────────────────────────────────────────
class GameController:

    def __init__(self):
        self.renderer = Renderer()
        self.state = "MENU"

        self.history: dict[str, dict[str, list[float]]] = {
            lbl: {"bt": [], "bf": []} for lbl, _ in PUZZLE_FILES
        }

        self.reset_run()

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset_run(self):
        self.current_file      = None
        self.current_label     = ""
        self.grid_bt           = [[0]*9 for _ in range(9)]
        self.grid_bf           = [[0]*9 for _ in range(9)]
        self.initial_mask      = [[False]*9 for _ in range(9)]
        self.timer_val         = 0.0
        self.start_time        = 0.0
        self.finish_bt         = False
        self.finish_bf         = False
        self.time_bt           = 0.0
        self.time_bf           = 0.0
        self.cd_start          = 0.0
        self._cb_count_bt      = 0
        self._cb_count_bf      = 0
        self._terminal_printed = False

    # ── Chargement ────────────────────────────────────────────────────────────

    def load_puzzle(self, label: str, filepath: str):
        self.current_file  = filepath
        self.current_label = label
        path = os.path.join(DATA_DIR, filepath)
        sg = SudokuGrid.from_file(path)
        self.grid_bt      = copy.deepcopy(sg.grid)
        self.grid_bf      = copy.deepcopy(sg.grid)
        self.initial_mask = copy.deepcopy(sg.initial_mask)

    # ── Threads algo ──────────────────────────────────────────────────────────

    def _run_bt(self):
        path = os.path.join(DATA_DIR, self.current_file)
        sg   = SudokuGrid.from_file(path)

        def cb(grid):
            self._cb_count_bt += 1
            if self._cb_count_bt % _VISUAL_THROTTLE == 0:
                self.grid_bt = [row[:] for row in grid]

        result, elapsed = sg.solve_backtracking(callback=cb)
        self.time_bt = elapsed
        if result:
            self.grid_bt = result.grid
        self.finish_bt = True

    def _run_bf(self):
        path = os.path.join(DATA_DIR, self.current_file)
        sg   = SudokuGrid.from_file(path)

        def cb(grid):
            self._cb_count_bf += 1
            if self._cb_count_bf % _VISUAL_THROTTLE == 0:
                self.grid_bf = [row[:] for row in grid]

        result, elapsed = sg.solve_brute_force(callback=cb)
        self.time_bf = elapsed
        if result:
            self.grid_bf = result.grid
        self.finish_bf = True

    def _save_to_history(self):
        if self.current_label and self.current_label in self.history:
            if self.time_bt > 0:
                self.history[self.current_label]["bt"].append(self.time_bt)
            if self.time_bf > 0:
                self.history[self.current_label]["bf"].append(self.time_bf)

    # ─────────────────────────────────────────────────────────────────────────
    #  Boucle principale
    # ─────────────────────────────────────────────────────────────────────────

    def run(self):
        saved = False
        while True:
            self.renderer.tick()
            mx, my, click, should_quit = self.renderer.poll_events()
            if should_quit:
                self.renderer.quit()
                sys.exit()

            if self.state == "MENU":
                saved = False
                action = self.renderer.draw_menu(mx, my, click, PUZZLE_FILES)
                if action == "STATS":
                    self.state = "STATS"
                elif action is not None:
                    label, filepath = action
                    self.reset_run()
                    self.load_puzzle(label, filepath)
                    self.state    = "COUNTDOWN"
                    self.cd_start = time.time()

            elif self.state == "COUNTDOWN":
                done = self.renderer.draw_countdown(
                    self.grid_bt, self.grid_bf, self.initial_mask,
                    self.current_label, time.time() - self.cd_start)
                if done:
                    self.start_time = time.time()
                    self.state      = "DUEL"
                    threading.Thread(target=self._run_bt, daemon=True).start()
                    threading.Thread(target=self._run_bf, daemon=True).start()

            elif self.state == "DUEL":
                if not (self.finish_bt and self.finish_bf):
                    self.timer_val = time.time() - self.start_time
                else:
                    if not saved:
                        self._save_to_history()
                        saved = True
                        if not self._terminal_printed:
                            self._terminal_printed = True
                            _print_duel_terminal(
                                self.current_label,
                                self.grid_bt,
                                self.grid_bf,
                                self.initial_mask,
                                self.time_bt,
                                self.time_bf,
                            )
                    self.state = "RESULTS"
                self.renderer.draw_duel(
                    self.grid_bt, self.grid_bf, self.initial_mask,
                    self.current_label, self.timer_val,
                    self.finish_bt, self.finish_bf)

            elif self.state == "RESULTS":
                h_data = self.history.get(self.current_label, {"bt": [], "bf": []})
                action = self.renderer.draw_results(
                    mx, my, click, self.current_label,
                    self.time_bt, self.time_bf, self.timer_val, h_data)
                if action == "REPLAY":
                    lbl, fp = self.current_label, self.current_file
                    self.reset_run()
                    self.load_puzzle(lbl, fp)
                    self.state    = "COUNTDOWN"
                    self.cd_start = time.time()
                elif action == "STATS":
                    self.state = "STATS"
                elif action == "MENU":
                    self.reset_run()
                    self.state = "MENU"

            elif self.state == "STATS":
                if self.renderer.draw_stats(mx, my, click, PUZZLE_FILES, self.history):
                    self.state = "MENU"

            self.renderer.flip()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    GameController().run()
