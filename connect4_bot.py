"""
Connect-4 bot using minimax with alpha-beta pruning,
a DEPTH LIMIT and a SCORING RULE for unfinished boards.

You are X, the bot is O. Drop a piece by typing a column number 1-7.
Run:  python connect4_bot.py

What is new compared with the tic-tac-toe bot:
  1. Depth limit  - the bot only looks DEPTH moves ahead, not to the end.
  2. Scoring rule - when it stops early, it estimates who is ahead.
  3. Move order   - it tries the centre columns first, so pruning cuts more.
"""
import math

ROWS, COLS = 6, 7
DEPTH = 5              # how many moves ahead the bot looks. Higher = stronger but slower.
SHOW_COMPARISON = True  # also run without pruning, to show how much work pruning saves

# Try the centre column first, then work outwards (centre moves are usually best)
MOVE_ORDER = [3, 2, 4, 1, 5, 0, 6]


def all_windows():
    """Every group of 4 cells in a line: horizontal, vertical and both diagonals.
    There are 69 of them. A player wins by filling any one."""
    windows = []
    for r in range(ROWS):
        for c in range(COLS):
            if c + 3 < COLS:                      # horizontal  -
                windows.append([(r, c + i) for i in range(4)])
            if r + 3 < ROWS:                      # vertical    |
                windows.append([(r + i, c) for i in range(4)])
            if r + 3 < ROWS and c + 3 < COLS:     # diagonal    \
                windows.append([(r + i, c + i) for i in range(4)])
            if r + 3 < ROWS and c - 3 >= 0:       # diagonal    /
                windows.append([(r + i, c - i) for i in range(4)])
    return windows


WINDOWS = all_windows()


def new_board():
    # board[0] is the TOP row, board[5] is the BOTTOM row
    return [[" "] * COLS for _ in range(ROWS)]


def free_columns(board):
    """Columns that still have space, centre first."""
    return [c for c in MOVE_ORDER if board[0][c] == " "]


def drop(board, col, piece):
    """Drop a piece into a column. It falls to the lowest empty row.
    Returns the row it landed in (so we can undo it later)."""
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == " ":
            board[r][col] = piece
            return r


def winner(board):
    """Return 'X' or 'O' if someone has four in a row, 'draw' if the board is full,
    or None if the game is still going."""
    for w in WINDOWS:
        first = board[w[0][0]][w[0][1]]
        if first != " " and all(board[r][c] == first for r, c in w):
            return first
    if all(board[0][c] != " " for c in range(COLS)):
        return "draw"
    return None


def estimate(board):
    """THE SCORING RULE. Guess who is ahead on an unfinished board.

    Look at every group of 4 cells. A group that only one player has pieces in
    is still 'alive' for that player:
        3 pieces + 1 empty  = strong threat  (50 points)
        2 pieces + 2 empty  = some promise   (5 points)
        1 piece  + 3 empty  = a small start  (1 point)
    A group containing both players' pieces is dead and worth nothing.
    Bot's points count as plus, human's as minus.
    """
    points = {0: 0, 1: 1, 2: 5, 3: 50}
    score = 0
    for w in WINDOWS:
        cells = [board[r][c] for r, c in w]
        bot, human = cells.count("O"), cells.count("X")
        if human == 0:
            score += points[bot]
        elif bot == 0:
            score -= points[human]
    # Small bonus for pieces in the centre column: they take part in more groups
    for r in range(ROWS):
        if board[r][3] == "O":
            score += 3
        elif board[r][3] == "X":
            score -= 3
    return score


def minimax(board, depth_left, bot_turn, alpha, beta, prune, counter):
    """Same idea as tic-tac-toe, with one change: stop when depth_left hits 0
    and use estimate() instead of playing to the end."""
    counter[0] += 1

    result = winner(board)
    if result == "O":
        return 1_000_000 + depth_left      # win sooner = higher score
    if result == "X":
        return -1_000_000 - depth_left     # lose later = less bad
    if result == "draw":
        return 0
    if depth_left == 0:
        return estimate(board)             # out of thinking time: make an educated guess

    if bot_turn:
        best = -math.inf
        for col in free_columns(board):
            row = drop(board, col, "O")                 # try the move
            score = minimax(board, depth_left - 1, False, alpha, beta, prune, counter)
            board[row][col] = " "                       # undo it
            best = max(best, score)
            alpha = max(alpha, best)
            if prune and alpha >= beta:
                break
        return best
    else:
        best = math.inf
        for col in free_columns(board):
            row = drop(board, col, "X")
            score = minimax(board, depth_left - 1, True, alpha, beta, prune, counter)
            board[row][col] = " "
            best = min(best, score)
            beta = min(beta, best)
            if prune and alpha >= beta:
                break
        return best


def best_move(board, depth=DEPTH, prune=True):
    """Return (best column for the bot, number of positions examined)."""
    counter = [0]
    best_score = -math.inf
    move = None
    for col in free_columns(board):
        row = drop(board, col, "O")
        score = minimax(board, depth - 1, False, best_score, math.inf, prune, counter)
        board[row][col] = " "
        if score > best_score:
            best_score = score
            move = col
    return move, counter[0]


def show(board):
    print()
    for row in board:
        print("| " + " | ".join(cell if cell != " " else "." for cell in row) + " |")
    print("+" + "---+" * COLS)
    print("  " + "   ".join(str(c + 1) for c in range(COLS)))
    print()


def play():
    board = new_board()
    print(f"You are X, the bot is O. The bot looks {DEPTH} moves ahead.")
    show(board)

    while winner(board) is None:
        choice = input("Your column (1-7): ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= COLS or board[0][int(choice) - 1] != " ":
            print("Pick a column from 1 to 7 that is not full.")
            continue
        drop(board, int(choice) - 1, "X")
        if winner(board) is not None:
            break

        move, pruned_count = best_move(board, prune=True)
        message = f"Bot plays column {move + 1}. Positions checked: {pruned_count:,} with pruning"
        if SHOW_COMPARISON:
            _, plain_count = best_move(board, prune=False)
            message += f", {plain_count:,} without"
        drop(board, move, "O")
        print(message + ".")
        show(board)

    show(board)
    result = winner(board)
    print("It's a draw." if result == "draw" else f"{result} wins!")


if __name__ == "__main__":
    play()
