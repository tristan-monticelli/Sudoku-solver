import copy
import time

from model.sudoky_grid import SudokyGrid


def _build_constraint_sets(grid: list[list[int]]):
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


def _backtrack(grid, rows, cols, boxes, callback) -> bool:
    """MRV : choisit la case vide avec le moins de candidats possibles."""
    best = None
    best_count = 10
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                count = sum(
                    1 for n in range(1, 10)
                    if n not in rows[r] and n not in cols[c]
                    and n not in boxes[r // 3][c // 3]
                )
                if count == 0:
                    return False
                if count < best_count:
                    best_count = count
                    best = (r, c)
                    if count == 1:
                        break
        if best_count == 1:
            break

    if best is None:
        return True

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
        if _backtrack(grid, rows, cols, boxes, callback):
            return True
        grid[r][c] = 0
        rows[r].discard(n)
        cols[c].discard(n)
        boxes[br][bc].discard(n)
        if callback:
            callback(grid)

    return False


def solve_backtracking(sudoku_grid: SudokyGrid, callback=None) -> tuple:
    """
    Résout un Sudoku par backtracking + heuristique MRV.
    Retourne (SudokyGrid résolu, temps en secondes) ou (None, temps).
    """
    grid = copy.deepcopy(sudoku_grid.grid)
    rows, cols, boxes = _build_constraint_sets(grid)
    start = time.perf_counter()
    solved = _backtrack(grid, rows, cols, boxes, callback)
    elapsed = time.perf_counter() - start
    if solved:
        return SudokyGrid(grid, copy.deepcopy(sudoku_grid.initial_mask)), elapsed
    return None, elapsed
