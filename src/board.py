
from const  import *
from piece  import *
from square import Square
from move import Move

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(COLS)]
        self.last_move = None
        self._create()
        self._add_piece('white')
        self._add_piece('black')

    def calc_moves(self, piece: Piece, row, col):


        def pawn_moves():
            steps = 1 if piece.moved else 2

            #vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        # create a move
                        move = Move(initial, final)
                        piece.add_move(move)
                    else: break
                else: break

            #diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col -1, col +1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # create a move
                        move = Move(initial, final)
                        piece.add_move(move)

        def knight_moves():
            possible_moves = [
                (row-2, col+1),
                (row-2, col-1),

                (row+2, col+1),
                (row+2, col-1),

                (row-1, col+2),
                (row-1, col-2),

                (row+1, col+2),
                (row+1, col-2),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # New square of new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # Create new move
                        move = Move(initial, final)
                        piece.add_move(move)

        def straight_line_move(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):

                        # has friend piece ... break.
                        if self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break

                        # New square of possible new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # Create new possible move
                        move = Move(initial, final)

                        # empty ... continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            piece.add_move(move)

                        # has enemy piece ... add move then break.
                        if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            piece.add_move(move)
                            break

                    # Not in range
                    else:
                        break
                    # incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            possible_moves = [
                (row - 1, col),  # up
                (row -1, col +1), #up right
                (row, col +1),  # right
                (row +1, col +1), #down right
                (row +1, col),  # down
                (row +1, col -1), #down left
                (row, col -1),  # left
                (row -1, col -1), #up left
            ]

            # Normal moves
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # New square of new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # Create new move
                        move = Move(initial, final)
                        piece.add_move(move)

            # Castling moves

        if isinstance(piece, Pawn):
            pawn_moves()
        elif isinstance(piece, Knight):
            knight_moves()
        elif isinstance(piece, Bishop):
            straight_line_move([
                (-1, 1), #up right
                (-1, -1), #up left
                (1, 1), #down right
                (1, -1), #down left
            ])
        elif isinstance(piece, Rook):
            straight_line_move([
                (-1, 0), #up
                (1, 0), #down
                (0, 1), #right
                (0, -1), #left
            ])
        elif isinstance(piece, Queen):
            straight_line_move([
                (-1, 1), #up right
                (-1, -1), #up left
                (1, 1), #down right
                (1, -1), #down left
                (-1, 0),  # up
                (1, 0),  # down
                (0, 1),  # right
                (0, -1),  # left

            ])
        elif isinstance(piece, King):
            king_moves()

    def move(self, piece: Piece, move: Move):
        initial = move.initial
        final = move.final

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # Set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves
    def _create(self):

        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_piece(self, color):
        row_pawn, row_other = (6,7) if color == 'white' else (1,0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # Bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # rooks
        self.squares[row_other][4] = Square(row_other, 4, King(color))
