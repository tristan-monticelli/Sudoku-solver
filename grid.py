"""
grid.py
-------
Classe SudokuGrid — résolution orientée objet d'un Sudoku 9x9.
"""

import copy
import time

# ── Codes ANSI pour distinguer valeurs initiales / résolues ──────────────────
_RESET  = "\033[0m"
_BOLD   = "\033[1m"          # valeurs données au départ (blanc gras)
_CYAN   = "\033[96m"         # valeurs trouvées par backtracking
_YELLOW = "\033[93m"         # valeurs trouvées par brute force


class SudokuGrid:
    def __init__(self, grid: list[list[int]], initial_mask: list[list[bool]] = None):
        self.grid = grid
        if initial_mask is None:
            self.initial_mask = [[cell != 0 for cell in row] for row in grid]
        else:
            self.initial_mask = initial_mask

    @classmethod
    def from_file(cls, filepath: str) -> "SudokuGrid":
        grid = []
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = [int(c) if c.isdigit() else 0 for c in line]
                if len(row) == 9:
                    grid.append(row)
        if len(grid) != 9:
            raise ValueError(f"Fichier invalide '{filepath}' : 9 lignes attendues.")
        return cls(grid)

    def display(self, solved_color: str = _CYAN, title: str = "") -> None:
        if title:
            print(f"\n  {_BOLD}{title}{_RESET}")
        print("  ┌───────┬───────┬───────┐")
        for r in range(9):
            if r in (3, 6):
                print("  ├───────┼───────┼───────┤")
            row_str = "  │"
            for c in range(9):
                if c in (3, 6):
                    row_str += "│"
                val = self.grid[r][c]
                if val == 0:
                    row_str += " · "
                elif self.initial_mask[r][c]:
                    row_str += f" {_BOLD}{val}{_RESET} "
                else:
                    row_str += f" {solved_color}{val}{_RESET} "
            row_str += "│"
            print(row_str)
        print("  └───────┴───────┴───────┘")

    def is_valid(self, r: int, c: int, n: int, grid: list[list[int]]) -> bool:
        if n in grid[r]:
            return False
        if n in [grid[i][c] for i in range(9)]:
            return False
        rs, cs = (r // 3) * 3, (c // 3) * 3
        for i in range(rs, rs + 3):
            for j in range(cs, cs + 3):
                if grid[i][j] == n:
                    return False
        return True

    # ── Helpers internes : sets de contraintes ────────────────────────────────

    @staticmethod
    def _build_constraint_sets(grid: list[list[int]]) -> tuple[
        list[set], list[set], list[list[set]]
    ]:
        """
        Construit 3 structures de lookup O(1) pour les contraintes :
          - rows[r]      : valeurs déjà placées sur la ligne r
          - cols[c]      : valeurs déjà placées sur la colonne c
          - boxes[r][c]  : valeurs déjà placées dans le bloc 3x3 de (r,c)

        Complexité : O(81) à la construction, puis O(1) par vérification.
        Sans sets : is_valid() parcourt lignes/colonnes/blocs → O(27) par test.
        Avec sets  : membership test → O(1) par test.
        """
        rows  = [set() for _ in range(9)]
        cols  = [set() for _ in range(9)]
        boxes = [[set() for _ in range(3)] for _ in range(3)]

        for r in range(9):
            for c in range(9):
                v = grid[r][c]
                if v:
                    rows[r].add(v)
                    cols[c].add(v)
                    boxes[r // 3][c // 3].add(v)

        return rows, cols, boxes

    # ── BACKTRACKING + MRV ──────────────────────────────────────────────────────
    #
    # Différence avec la brute force :
    #   - Pas de liste pré-calculée : scanne dynamiquement la grille à chaque appel
    #   - Heuristique MRV (Minimum Remaining Values) : choisit la case vide
    #     ayant le moins de valeurs possibles → élague massivement l'arbre
    #   - Sets de contraintes O(1) pour les vérifications
    #
    # La brute force parcourt les cases dans un ordre fixe (gauche→droite,
    # haut→bas). Le backtracking+MRV choisit toujours la case la plus
    # contrainte, ce qui réduit le nombre de branches explorées.

    def solve_backtracking(self, callback=None) -> tuple["SudokuGrid | None", float]:
        grid = copy.deepcopy(self.grid)
        rows, cols, boxes = self._build_constraint_sets(grid)

        start = time.perf_counter()
        solved = self._backtrack(grid, rows, cols, boxes, callback)
        elapsed = time.perf_counter() - start
        if solved:
            return SudokuGrid(grid, copy.deepcopy(self.initial_mask)), elapsed
        return None, elapsed

    def _backtrack(self, grid, rows, cols, boxes, callback) -> bool:
        # MRV : trouver dynamiquement la case vide avec le moins de candidats
        best = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    count = 0
                    for n in range(1, 10):
                        if n not in rows[r] and n not in cols[c] and n not in boxes[r // 3][c // 3]:
                            count += 1
                    if count == 0:
                        return False  # case vide sans candidat → dead end
                    if count < best_count:
                        best_count = count
                        best = (r, c)
                        if count == 1:
                            break  # on ne fera pas mieux
            if best_count == 1:
                break

        if best is None:
            return True  # plus de case vide → résolu

        r, c = best
        br, bc = r // 3, c // 3

        for n in range(1, 10):
            if n in rows[r] or n in cols[c] or n in boxes[br][bc]:
                continue

            grid[r][c] = n
            rows[r].add(n)
            cols[c].add(n)
            boxes[br][bc].add(n)

            if callback:
                callback(grid)

            if self._backtrack(grid, rows, cols, boxes, callback):
                return True

            grid[r][c] = 0
            rows[r].discard(n)
            cols[c].discard(n)
            boxes[br][bc].discard(n)

            if callback:
                callback(grid)

        return False

    # ── BRUTE FORCE ─────────────────────────────────────────────────────────────
    #
    # Différence avec le backtracking :
    #   - Scan dynamique en ordre fixe (gauche→droite, haut→bas) :
    #     prend la PREMIÈRE case vide trouvée, sans heuristique
    #   - Sets de contraintes O(1) pour les vérifications
    #   - Pas de MRV → explore plus de branches que le backtracking

    def solve_brute_force(self, callback=None) -> tuple["SudokuGrid | None", float]:
        grid = copy.deepcopy(self.grid)
        rows, cols, boxes = self._build_constraint_sets(grid)

        start   = time.perf_counter()
        solved  = self._brute_force(grid, rows, cols, boxes, callback)
        elapsed = time.perf_counter() - start

        if solved:
            return SudokuGrid(grid, copy.deepcopy(self.initial_mask)), elapsed
        return None, elapsed

    def _brute_force(self, grid, rows, cols, boxes, callback) -> bool:
        # Ordre fixe : première case vide trouvée (gauche→droite, haut→bas)
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    br, bc = r // 3, c // 3

                    for n in range(1, 10):
                        if n in rows[r] or n in cols[c] or n in boxes[br][bc]:
                            continue

                        grid[r][c] = n
                        rows[r].add(n)
                        cols[c].add(n)
                        boxes[br][bc].add(n)

                        if callback:
                            callback(grid)

                        if self._brute_force(grid, rows, cols, boxes, callback):
                            return True

                        grid[r][c] = 0
                        rows[r].discard(n)
                        cols[c].discard(n)
                        boxes[br][bc].discard(n)

                        if callback:
                            callback(grid)

                    return False
        return True
