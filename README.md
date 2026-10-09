# Connect 4 Bot: Depth-Limited Minimax with Alpha-Beta Pruning

A command-line Connect 4 game where you play against a bot. The bot uses minimax with alpha-beta pruning, like a tic-tac-toe bot, but Connect 4 has far too many possible games to search to the end. So this bot looks a fixed number of moves ahead and then uses a scoring rule to judge who is winning on the unfinished board.

After every move, the bot reports how many positions it checked with and without pruning.

## How to play

You need Python 3. There are no other libraries to install.

```bash
python connect4_bot.py
```

You are X and move first; the bot is O. Type a column number from 1 to 7 to drop your piece, and it falls to the lowest empty row. Connect four in a row horizontally, vertically, or diagonally to win.

```
| . | . | . | . | . | . | . |
| . | . | . | . | . | . | . |
| . | . | . | . | . | . | . |
| . | . | . | . | . | . | . |
| . | . | . | O | . | . | . |
| . | . | . | X | . | . | . |
+---+---+---+---+---+---+---+
  1   2   3   4   5   6   7
```

## What's different from tic-tac-toe

Tic-tac-toe is small enough to search every possible game to the end. Connect 4 has around 4.5 trillion reachable positions, so a full search is out of reach. The bot adds three ideas:

**1. Depth limit**

The bot only looks `DEPTH` moves ahead (5 by default) instead of playing every line to the end.

**2. Scoring rule for unfinished boards**

When the search stops before the game is over, `estimate()` judges the position. It looks at all 69 groups of four cells in a line (horizontal, vertical, and both diagonals). A group that holds pieces from only one player can still become a win for that player:

| Pieces in the group | Points |
|---|---|
| 3 pieces + 1 empty cell | 50 |
| 2 pieces + 2 empty cells | 5 |
| 1 piece + 3 empty cells | 1 |

A group holding both players' pieces can never be completed, so it scores nothing. The bot's points count as positive and yours as negative. Each piece in the centre column adds 3 more, because the centre is part of more groups than any other column.

Finished games are scored as ±1,000,000, adjusted by depth so the bot prefers faster wins and slower losses.

**3. Move ordering**

The bot tries the centre column first and works outwards (4, 3, 5, 2, 6, 1, 7). Strong moves tend to be near the centre, and examining good moves first lets alpha-beta pruning cut off more branches early.

## Results

**Pruning.** Positions examined for the bot's first reply at depth 5:

| Your opening move | Bot's reply | Without pruning | With pruning | Reduction |
|---|---|---|---|---|
| Column 4 (centre) | Column 4 | 19,607 | 697 | 96% |
| Column 1 (edge) | Column 4 | 19,607 | 947 | 95% |

**Search depth and speed.** Positions examined with pruning for the first reply, after you open in the centre:

| Depth | Positions | Time |
|---|---|---|
| 3 | 75 | under 0.01 s |
| 4 | 452 | 0.01 s |
| 5 | 697 | 0.02 s |
| 6 | 5,559 | 0.12 s |
| 7 | 6,993 | 0.13 s |

Even at depth 7 the bot replies almost instantly, so there is room to make it stronger.

**Strength.** Results over test games, with the bot playing second at depth 5:

| Opponent (moves first) | Games | Bot wins | Opponent wins | Draws |
|---|---|---|---|---|
| Random moves | 100 | 100 | 0 | 0 |
| The same bot at depth 1 | 30 | 29 | 0 | 1 |
| The same bot at depth 3 | 30 | 19 | 11 | 0 |

In the games between bots, the first two moves were random so the games would differ. Unlike the tic-tac-toe bot, this one can be beaten, because it cannot see past its depth limit.

## Settings

Two values at the top of `connect4_bot.py` change how the bot behaves:

| Setting | Default | Effect |
|---|---|---|
| `DEPTH` | 5 | How many moves ahead the bot looks. Higher is stronger but slower. |
| `SHOW_COMPARISON` | `True` | Also runs the search without pruning after each move, to report the difference. Set to `False` for faster replies at higher depths. |

## Code structure

Everything is in `connect4_bot.py`:

| Function | Purpose |
|---|---|
| `all_windows()` | Lists all 69 groups of four cells in a line |
| `drop(board, col, piece)` | Drops a piece into a column and returns the row it landed in |
| `free_columns(board)` | Returns the columns that aren't full, centre first |
| `winner(board)` | Returns `"X"`, `"O"`, `"draw"`, or `None` if the game is still going |
| `estimate(board)` | The scoring rule for unfinished boards |
| `minimax(...)` | Depth-limited minimax with optional alpha-beta pruning, counting the positions it visits |
| `best_move(board, depth, prune)` | Returns the best column and the number of positions examined |
| `show(board)` | Prints the board with column numbers |
| `play()` | Runs the game loop |

## Possible improvements

- Let the player choose to go first or second
- Use iterative deepening: search depth 1, then 2, and so on until a time limit runs out
- Cache positions already scored, since different move orders often reach the same board
- Tune the points in the scoring rule, for example by playing versions against each other
- Build a graphical version with Pygame or Streamlit

## Author

Payal Satapathy
