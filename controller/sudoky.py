import time
import threading
import copy
import sys
import os
import random

from model.sudoky_grid import SudokyGrid
from algoritms.backtracking import solve_backtracking
from algoritms.force_brude import solve_brute_force
from view.display_sudoku import DisplaySudoku
from view.menu import Menu

# ── Codes ANSI terminal ───────────────────────────────────────────────────────
_R  = "\033[0m"
_B  = "\033[1m"
_CY = "\033[96m"
_YL = "\033[93m"
_GR = "\033[92m"
_GY = "\033[90m"
_MG = "\033[95m"

# ── Config ────────────────────────────────────────────────────────────────────
PUZZLE_CATEGORIES = [
    ("NORMAL",    ["sudoku.txt", "sudoku2.txt", "sudoku3.txt", "sudoku4.txt"]),
    ("DIFFICILE", ["evilsudoku.txt"]),
    ("RACE",      ["race.txt"]),
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

_VISUAL_THROTTLE = 500


# ── Terminal display ──────────────────────────────────────────────────────────

def _fmt_time(t: float) -> str:
    if t <= 0:  return "—"
    if t >= 60: return f"{t/60:.1f} min"
    if t >= 1:  return f"{t:.3f} s"
    return f"{t*1000:.2f} ms"


def _print_duel_terminal(label, grid_bt, grid_bf, initial_mask, time_bt, time_bf):
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

    PAD      = 38
    bt_lines = build_grid_lines(grid_bt, initial_mask, _CY)
    bf_lines = build_grid_lines(grid_bf, initial_mask, _YL)

    print(f"\n{_B}{_MG}{'═' * 74}{_R}")
    print(f"{_B}{_MG}  SUDOKU DUEL  —  {label}{_R}")
    print(f"{_B}{_MG}{'═' * 74}{_R}\n")
    print(pad_to(f"  {_CY}{_B}BACKTRACKING{_R}", PAD + 14) + f"     {_YL}{_B}BRUTE FORCE{_R}")
    print(f"  {_GY}{'─' * (PAD - 2)}{_R}     {_GY}{'─' * (PAD - 2)}{_R}")
    for bt_l, bf_l in zip(bt_lines, bf_lines):
        print(pad_to(bt_l, PAD + 14) + "     " + bf_l)

    bt_faster = time_bt <= time_bf
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


# ── GameController ────────────────────────────────────────────────────────────

class GameController:

    def __init__(self):
        self.display = DisplaySudoku()
        self.menu    = Menu(self.display.screen)
        self.state   = "MENU"

        self.history: dict = {
            cat: {"bt": [], "bf": []} for cat, _ in PUZZLE_CATEGORIES
        }
        self.reset_run()

    def reset_run(self):
        self.current_file      = None
        self.current_label     = ""
        self.grid_bt           = [[0] * 9 for _ in range(9)]
        self.grid_bf           = [[0] * 9 for _ in range(9)]
        self.initial_mask      = [[False] * 9 for _ in range(9)]
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

    def load_puzzle(self, category: str):
        for cat, files in PUZZLE_CATEGORIES:
            if cat == category:
                filepath = random.choice(files)
                break
        self.current_file  = filepath
        self.current_label = category
        path = os.path.join(DATA_DIR, filepath)
        sg = SudokyGrid.from_file(path)
        self.grid_bt      = copy.deepcopy(sg.grid)
        self.grid_bf      = copy.deepcopy(sg.grid)
        self.initial_mask = copy.deepcopy(sg.initial_mask)

    def _run_bt(self):
        path = os.path.join(DATA_DIR, self.current_file)
        sg   = SudokyGrid.from_file(path)

        def cb(grid):
            self._cb_count_bt += 1
            if self._cb_count_bt % _VISUAL_THROTTLE == 0:
                self.grid_bt = [row[:] for row in grid]

        result, elapsed = solve_backtracking(sg, callback=cb)
        self.time_bt = elapsed
        if result:
            self.grid_bt = result.grid
        self.finish_bt = True

    def _run_bf(self):
        path = os.path.join(DATA_DIR, self.current_file)
        sg   = SudokyGrid.from_file(path)

        def cb(grid):
            self._cb_count_bf += 1
            if self._cb_count_bf % _VISUAL_THROTTLE == 0:
                self.grid_bf = [row[:] for row in grid]

        result, elapsed = solve_brute_force(sg, callback=cb)
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

    def run(self):
        saved = False
        while True:
            self.display.tick()
            mx, my, click, should_quit = self.display.poll_events()
            if should_quit:
                self.display.quit()
                sys.exit()

            if self.state == "MENU":
                saved  = False
                action = self.menu.draw_menu(mx, my, click, PUZZLE_CATEGORIES)
                if action == "STATS":
                    self.state = "STATS"
                elif action is not None:
                    self.reset_run()
                    self.load_puzzle(action)
                    self.state    = "COUNTDOWN"
                    self.cd_start = time.time()

            elif self.state == "COUNTDOWN":
                done = self.display.draw_countdown(
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
                                self.grid_bt, self.grid_bf,
                                self.initial_mask,
                                self.time_bt, self.time_bf,
                            )
                    self.state = "RESULTS"
                self.display.draw_duel(
                    self.grid_bt, self.grid_bf, self.initial_mask,
                    self.current_label, self.timer_val,
                    self.finish_bt, self.finish_bf)

            elif self.state == "RESULTS":
                h_data = self.history.get(self.current_label, {"bt": [], "bf": []})
                action = self.display.draw_results(
                    mx, my, click, self.current_label,
                    self.time_bt, self.time_bf, self.timer_val, h_data)
                if action == "REPLAY":
                    cat = self.current_label
                    self.reset_run()
                    self.load_puzzle(cat)
                    self.state    = "COUNTDOWN"
                    self.cd_start = time.time()
                elif action == "STATS":
                    self.state = "STATS"
                elif action == "MENU":
                    self.reset_run()
                    self.state = "MENU"

            elif self.state == "STATS":
                if self.display.draw_stats(mx, my, click, PUZZLE_CATEGORIES, self.history):
                    self.state = "MENU"

            self.display.flip()
