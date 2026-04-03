# Game Instructions

- Working on AI gamemode...

* Install dependency: `py -m pip install pygame`
* Run game: `py src/main.py`
* Press 't' to change theme (green, brown, blue, gray)
* Press 'r' to restart the game
* On pawn promotion, click a piece in the dialog or press Q / R / B / N
* Run tests: `py -m unittest discover -s tests -v`

## Implemented Features

- Turn enforcement (white/black alternate)
- Check, checkmate, and stalemate detection
- Castling (both sides when legal)
- En passant (including one-move eligibility)
- Pawn promotion (auto-promote to queen)
- Pawn promotion selection dialog (Queen, Rook, Bishop, Knight)
- Last-move highlight and square hover outline
- Board coordinates on all themes
- In-game status overlay and move history panel

# Game Snapshots

## Snapshot 1 - Start (green)

![snapshot1](snapshots/snapshot1.png)

## Snapshot 2 - Start (brown)

![snapshot2](snapshots/snapshot2.png)

## Snapshot 3 - Start (blue)

![snapshot3](snapshots/snapshot3.png)

## Snapshot 4 - Start (gray)

![snapshot4](snapshots/snapshot4.png)

## Snapshot 5 - Valid Moves

![snapshot5](snapshots/snapshot5.png)

## Snapshot 6 - Castling

![snapshot6](snapshots/snapshot6.png)
