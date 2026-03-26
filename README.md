# 🧩 Sudoku Duel — Backtracking vs Brute Force

Interface visuelle Pygame qui fait s'affronter deux algorithmes de résolution de sudoku en temps réel, côte à côte.

---

## 📁 Structure du projet

```
sudoku-duel/
├── main.py               # Contrôleur de jeu, threads, affichage terminal
├── visuel.py             # Rendu Pygame (classe Renderer)
├── grid.py               # Grille + algorithmes de résolution (SudokuGrid)
├── data/
│   ├── sudoku.txt        # Facile
│   ├── sudoku2.txt       # Moyen
│   ├── sudoku3.txt       # Difficile
│   ├── sudoku4.txt       # Difficile+
│   └── evilsudoku.txt    # Evil
└── README.md
```

---

## 🚀 Lancement

```bash
pip install pygame
python main.py
```

---

## 🎮 Fonctionnement

1. **Menu** — choisis un puzzle parmi 5 niveaux
2. **Countdown** — décompte 3-2-1
3. **Duel** — les deux algos tournent en parallèle (threads), la grille se remplit en live
4. **Résultats** — podium, temps, complexité, et comparaison des performances
5. **Stats** — moyennes par niveau sur la session en cours

---

## ⚙️ Les deux algorithmes

### Backtracking (`solve_backtracking`)

Algorithme récursif classique. À chaque case vide, il teste les valeurs 1-9 et n'explore que les branches valides grâce à `is_valid()`. Si une branche échoue, il revient en arrière (*backtrack*).

- Complexité : **O(9^N)** dans le pire cas, mais les contraintes élaguent massivement l'espace de recherche
- En pratique : très rapide, même sur les grilles "Evil"

### Brute Force (`solve_brute_force`)

Même principe de backtracking, mais avec une structure de données différente pour les vérifications de contraintes.

#### Ancienne version (lente ❌)

```python
# Vérifie la ligne, colonne et bloc en parcourant des listes → O(27) par test
if n in grid[r]:           # O(9)
if n in [grid[i][c] ...]   # O(9)
for i in range(...):       # O(9)
```

Pire encore : l'ancienne implémentation **ne vérifiait pas les contraintes à chaque étape** — elle posait les chiffres et validait la grille entière une fois complète. Résultat : un espace de recherche de **9^55** sur un Evil sudoku (~55 cases vides). Impossible en temps raisonnable.

#### Nouvelle version (optimisée ✅)

```python
# 3 sets de contraintes construits une seule fois en O(81)
rows[r], cols[c], boxes[r//3][c//3]

# Vérification O(1) par membership test (hash lookup)
if n in rows[r] or n in cols[c] or n in boxes[br][bc]:
    continue
```

Les sets sont **mis à jour dynamiquement** à chaque pose/retrait de chiffre. Cela permet d'élaguer les branches invalides immédiatement, comme le BT, mais avec un overhead de lookup minimal.

| Opération | Liste | Set |
|-----------|-------|-----|
| Recherche `n in x` | O(n) | **O(1)** |
| Ajout | O(1) | O(1) |
| Suppression | O(n) | **O(1)** |

**Gain mesuré sur `evilsudoku.txt` : ~200x plus rapide.**

---

## 📊 Complexité algorithmique

| Algorithme | Complexité théorique | Lookups |
|------------|----------------------|---------|
| Backtracking | O(9^N) élagué | O(27) par test (listes) |
| Brute Force (avant) | O(9^N) non élagué | aucun (validation finale) |
| **Brute Force (après)** | **O(9^N) élagué** | **O(1) par test (sets)** |

> **N** = nombre de cases vides. Sur un Sudoku Evil, N ≈ 55.

En pratique, les deux algorithmes atteignent des performances similaires après optimisation — la différence visible en duel vient principalement de l'ordre d'exploration (identique ici) et des constantes cachées.

---

## 🎨 Affichage

- **Blanc gras** — valeurs données dans le puzzle original
- **Cyan** — valeurs trouvées par le Backtracking
- **Jaune** — valeurs trouvées par la Brute Force
- Le chronomètre central tourne jusqu'à ce que les deux algos aient terminé

---

## 📈 Page Stats

Accessible depuis le menu ou l'écran résultats. Affiche pour chaque niveau :
- Temps moyen Backtracking
- Temps moyen Brute Force
- Nombre de runs effectués sur la session
- Speedup global BT vs BF

> Les stats sont en mémoire (session uniquement) — pas de persistance fichier.

---

## 🧠 Concepts clés (cours La Plateforme)

Ce projet illustre plusieurs notions d'algorithmique :

- **Récursivité** — les deux solveurs s'appellent eux-mêmes jusqu'au cas de base (grille complète ou aucune case vide)
- **Backtracking** — exploration avec retour en arrière sur les branches invalides
- **Complexité temporelle** — comparaison O(9^N) élagué vs non élagué
- **Structures de données** — impact concret des listes O(n) vs sets O(1) sur les performances
- **Pile d'appels** — chaque appel récursif empile un état ; Python peut atteindre la limite (`RecursionError`) sur des grilles extrêmes
