
from const  import *
from piece  import *
from square import Square
from move import Move

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(COLS)]
        self.last_move = None
        self.pending_promotion = None
        self.move_history = []
        self._create()
        self._add_piece('white')
        self._add_piece('black')

    def calc_moves(self, piece: Piece, row, col):
        piece.clear_moves()


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

            # en passant moves
            en_passant_row = 3 if piece.color == 'white' else 4
            if row == en_passant_row:
                for adjacent_col in [col - 1, col + 1]:
                    if Square.in_range(adjacent_col):
                        adjacent_square = self.squares[row][adjacent_col]
                        if adjacent_square.has_enemy_piece(piece.color) and isinstance(adjacent_square.piece, Pawn):
                            if adjacent_square.piece.en_passant:
                                initial = Square(row, col)
                                final = Square(row + piece.dir, adjacent_col)
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
            if piece.moved or self.is_in_check(piece.color):
                return

            enemy_color = 'black' if piece.color == 'white' else 'white'

            # Kingside castling
            right_rook_square = self.squares[row][7]
            if right_rook_square.has_team_piece(piece.color) and isinstance(right_rook_square.piece, Rook):
                right_rook = right_rook_square.piece
                if not right_rook.moved:
                    if self.squares[row][5].isempty() and self.squares[row][6].isempty():
                        if not self.is_square_attacked(row, 5, enemy_color) and not self.is_square_attacked(row, 6, enemy_color):
                            initial = Square(row, col)
                            final = Square(row, col + 2)
                            move = Move(initial, final)
                            piece.add_move(move)

            # Queenside castling
            left_rook_square = self.squares[row][0]
            if left_rook_square.has_team_piece(piece.color) and isinstance(left_rook_square.piece, Rook):
                left_rook = left_rook_square.piece
                if not left_rook.moved:
                    if self.squares[row][1].isempty() and self.squares[row][2].isempty() and self.squares[row][3].isempty():
                        if not self.is_square_attacked(row, 3, enemy_color) and not self.is_square_attacked(row, 2, enemy_color):
                            initial = Square(row, col)
                            final = Square(row, col - 2)
                            move = Move(initial, final)
                            piece.add_move(move)

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

        legal_moves = []
        for move in piece.moves:
            if not self.in_check_after_move(piece, move):
                legal_moves.append(move)
        piece.moves = legal_moves

    def move(self, piece: Piece, move: Move):
        initial = move.initial
        final = move.final

        self._reset_en_passant_flags()

        captured_piece = self.squares[final.row][final.col].piece
        is_en_passant = isinstance(piece, Pawn) and initial.col != final.col and self.squares[final.row][final.col].isempty()
        if is_en_passant:
            captured_piece = self.squares[initial.row][final.col].piece
            self.squares[initial.row][final.col].piece = None

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        is_castling = isinstance(piece, King) and abs(final.col - initial.col) == 2
        if isinstance(piece, King) and abs(final.col - initial.col) == 2:
            self._move_castling_rook(initial.row, initial.col, final.col)

        piece.moved = True

        promotion_pending = False
        if isinstance(piece, Pawn):
            if abs(final.row - initial.row) == 2:
                piece.en_passant = True
            if self._check_promotion(final):
                promotion_pending = True

        notation = self._build_move_notation(piece, initial, final, captured_piece is not None, is_castling, is_en_passant, promotion_pending)
        self.move_history.append(notation)
        if promotion_pending:
            self.pending_promotion = {
                'row': final.row,
                'col': final.col,
                'color': piece.color,
                'history_index': len(self.move_history) - 1
            }

        # clear valid moves
        piece.clear_moves()

        # Set last move
        self.last_move = move

    def has_pending_promotion(self):
        return self.pending_promotion is not None

    def promote_pawn(self, piece_name):
        if not self.pending_promotion:
            return False

        row = self.pending_promotion['row']
        col = self.pending_promotion['col']
        color = self.pending_promotion['color']
        history_index = self.pending_promotion['history_index']

        promotion_map = {
            'q': Queen,
            'r': Rook,
            'b': Bishop,
            'n': Knight
        }

        selected_class = promotion_map.get(piece_name.lower())
        if not selected_class:
            return False

        self.squares[row][col].piece = selected_class(color)
        self.move_history[history_index] = self.move_history[history_index].replace('=?', f'={piece_name.upper()}')
        self.pending_promotion = None
        return True

    def _check_promotion(self, final):
        return final.row == 0 or final.row == 7

    def _square_name(self, row, col):
        return f"{Square.get_alphacol(col)}{ROWS - row}"

    def _build_move_notation(self, piece, initial, final, captured, is_castling, is_en_passant, promotion_pending):
        if is_castling:
            return 'O-O' if final.col > initial.col else 'O-O-O'

        from_sq = self._square_name(initial.row, initial.col)
        to_sq = self._square_name(final.row, final.col)
        sep = 'x' if captured else '-'

        if isinstance(piece, Pawn):
            notation = f'{from_sq}{sep}{to_sq}'
        else:
            piece_symbol = piece.name[0].upper()
            if piece.name == 'knight':
                piece_symbol = 'N'
            notation = f'{piece_symbol}{from_sq}{sep}{to_sq}'

        if promotion_pending:
            notation += '=?'

        if is_en_passant:
            notation += ' e.p.'

        return notation

    def _reset_en_passant_flags(self):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece() and isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

    def _move_castling_rook(self, row, initial_col, final_col):
        if final_col > initial_col:
            rook_initial_col = 7
            rook_final_col = 5
        else:
            rook_initial_col = 0
            rook_final_col = 3

        rook = self.squares[row][rook_initial_col].piece
        self.squares[row][rook_initial_col].piece = None
        self.squares[row][rook_final_col].piece = rook
        if rook:
            rook.moved = True

    def in_check_after_move(self, piece: Piece, move: Move):
        initial = move.initial
        final = move.final

        captured_piece = self.squares[final.row][final.col].piece
        initial_moved_state = piece.moved
        en_passant_captured_piece = None
        rook = None
        rook_initial_col = None
        rook_final_col = None

        is_en_passant = isinstance(piece, Pawn) and initial.col != final.col and self.squares[final.row][final.col].isempty()
        if is_en_passant:
            en_passant_captured_piece = self.squares[initial.row][final.col].piece
            self.squares[initial.row][final.col].piece = None

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, King) and abs(final.col - initial.col) == 2:
            if final.col > initial.col:
                rook_initial_col = 7
                rook_final_col = 5
            else:
                rook_initial_col = 0
                rook_final_col = 3

            rook = self.squares[initial.row][rook_initial_col].piece
            self.squares[initial.row][rook_initial_col].piece = None
            self.squares[initial.row][rook_final_col].piece = rook

        piece.moved = True

        in_check = self.is_in_check(piece.color)

        self.squares[initial.row][initial.col].piece = piece
        self.squares[final.row][final.col].piece = captured_piece
        if is_en_passant:
            self.squares[initial.row][final.col].piece = en_passant_captured_piece
        if rook is not None:
            self.squares[initial.row][rook_final_col].piece = None
            self.squares[initial.row][rook_initial_col].piece = rook
        piece.moved = initial_moved_state

        return in_check

    def is_in_check(self, color):
        king_row, king_col = self._find_king(color)
        if king_row is None:
            return False

        enemy_color = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(king_row, king_col, enemy_color)

    def has_any_legal_move(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_team_piece(color):
                    piece = self.squares[row][col].piece
                    self.calc_moves(piece, row, col)
                    if piece.moves:
                        return True
        return False

    def is_square_attacked(self, target_row, target_col, by_color):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_team_piece(by_color):
                    piece = self.squares[row][col].piece
                    if self._piece_attacks_square(piece, row, col, target_row, target_col):
                        return True
        return False

    def _piece_attacks_square(self, piece, row, col, target_row, target_col):
        if isinstance(piece, Pawn):
            attack_row = row + piece.dir
            return attack_row == target_row and abs(col - target_col) == 1

        if isinstance(piece, Knight):
            row_diff = abs(row - target_row)
            col_diff = abs(col - target_col)
            return (row_diff, col_diff) in [(2, 1), (1, 2)]

        if isinstance(piece, King):
            row_diff = abs(row - target_row)
            col_diff = abs(col - target_col)
            return max(row_diff, col_diff) == 1

        if isinstance(piece, Bishop):
            return self._is_clear_diagonal(row, col, target_row, target_col)

        if isinstance(piece, Rook):
            return self._is_clear_straight(row, col, target_row, target_col)

        if isinstance(piece, Queen):
            return self._is_clear_straight(row, col, target_row, target_col) or self._is_clear_diagonal(row, col, target_row, target_col)

        return False

    def _is_clear_straight(self, row, col, target_row, target_col):
        if row != target_row and col != target_col:
            return False

        if row == target_row:
            step = 1 if target_col > col else -1
            for current_col in range(col + step, target_col, step):
                if self.squares[row][current_col].has_piece():
                    return False
            return True

        step = 1 if target_row > row else -1
        for current_row in range(row + step, target_row, step):
            if self.squares[current_row][col].has_piece():
                return False
        return True

    def _is_clear_diagonal(self, row, col, target_row, target_col):
        row_diff = target_row - row
        col_diff = target_col - col

        if abs(row_diff) != abs(col_diff):
            return False

        row_step = 1 if row_diff > 0 else -1
        col_step = 1 if col_diff > 0 else -1
        current_row = row + row_step
        current_col = col + col_step

        while current_row != target_row and current_col != target_col:
            if self.squares[current_row][current_col].has_piece():
                return False
            current_row += row_step
            current_col += col_step

        return True

    def _find_king(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_team_piece(color):
                    piece = self.squares[row][col].piece
                    if isinstance(piece, King):
                        return row, col

        return None, None

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
