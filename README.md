# Sudoku Duel — Backtracking vs Brute Force

Interface Pygame qui oppose deux algorithmes de resolution de Sudoku en temps reel, cote a cote.

---

## Structure du projet

```
Sudoku_Solver/
├── main.py            # Controleur de jeu, threads, affichage terminal
├── visuel.py          # Rendu Pygame (classe Renderer)
├── grid.py            # Grille + algorithmes de resolution (SudokuGrid)
├── data/
│   ├── sudoku.txt     # Facile
│   ├── sudoku2.txt    # Moyen
│   ├── sudoku3.txt    # Difficile
│   ├── sudoku4.txt    # Difficile+
│   ├── evilsudoku.txt # Evil
│   └── race.txt       # Race
└── README.md
```

---

## Lancement

```bash
pip install pygame
python main.py
```

---

## Fonctionnement

1. **Menu** — choix d'une categorie : Normal, Difficile ou Race
2. **Countdown** — decompte 3-2-1 avec apercu des grilles
3. **Duel** — les deux algorithmes tournent en parallele (threads), les grilles se remplissent en live
4. **Resultats** — podium, temps, complexite, ratio de vitesse et moyenne du niveau
5. **Stats** — tableau recapitulatif, diagramme en barres et moyennes globales sur la session

Un puzzle est tire au hasard dans la categorie choisie a chaque partie.

---

## Les deux algorithmes

### Backtracking + MRV (`solve_backtracking`)

Algorithme recursif avec heuristique **MRV** (Minimum Remaining Values) : a chaque etape, il choisit la case vide ayant le moins de candidats possibles, ce qui elague massivement l'arbre de recherche. Les contraintes (ligne, colonne, bloc) sont stockees dans des **sets** pour des verifications en O(1).

- Complexite : **O(9^N)** dans le pire cas, fortement reduite par le MRV
- En pratique : tres rapide, meme sur les grilles Evil

### Brute Force (`solve_brute_force`)

Meme principe de backtracking recursif, mais sans heuristique : les cases vides sont parcourues dans un **ordre fixe** (gauche vers droite, haut vers bas), sans choisir la plus contrainte. Utilise egalement des sets O(1) pour les verifications.

- Complexite : **O(9^N)** dans le pire cas
- En pratique : plus lent que le backtracking car il explore davantage de branches

### Comparaison

| | Backtracking + MRV | Brute Force |
|---|---|---|
| Ordre d'exploration | Case la plus contrainte (MRV) | Ordre fixe (gauche-droite, haut-bas) |
| Verification contraintes | Sets O(1) | Sets O(1) |
| Complexite theorique | O(9^N) elague | O(9^N) elague |
| Performance pratique | Plus rapide (moins de branches) | Plus lent (plus de branches) |

> **N** = nombre de cases vides. Sur un Sudoku Evil, N ~ 55.

---

## Categories de puzzles

| Categorie | Fichiers | Description |
|-----------|----------|-------------|
| **NORMAL** | `sudoku.txt`, `sudoku2.txt`, `sudoku3.txt`, `sudoku4.txt` | Facile a Difficile+ |
| **DIFFICILE** | `evilsudoku.txt` | Grilles Evil |
| **RACE** | `race.txt` | Mode course |

---

## Affichage

- **Blanc** — valeurs initiales du puzzle
- **Cyan** — valeurs trouvees par le Backtracking
- **Orange** — valeurs trouvees par la Brute Force
- Le chronometre central tourne jusqu'a ce que les deux algorithmes aient termine

---

## Page Stats

Accessible depuis le menu ou l'ecran resultats :

- Tableau des temps moyens par categorie (BT vs BF)
- Diagramme en barres groupe
- Moyenne globale et ratio de vitesse BT/BF sur la session

> Les stats sont en memoire (session uniquement) — pas de persistance fichier.

---

## Concepts cles

- **Recursivite** — les deux solveurs s'appellent eux-memes jusqu'au cas de base
- **Backtracking** — exploration avec retour en arriere sur les branches invalides
- **Heuristique MRV** — choix de la case la plus contrainte pour reduire l'espace de recherche
- **Structures de donnees** — impact des sets O(1) vs listes O(n) sur les performances
- **Multithreading** — execution parallele des deux algorithmes via `threading.Thread`
