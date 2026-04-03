import copy


class AI:
    def __init__(self, color='black'):
        self.color = color

    def choose_move(self, board):
        candidates = board.get_all_legal_moves(self.color)
        if not candidates:
            return None

        best_score = None
        best_choice = None

        for piece, move, row, col in candidates:
            sim_board = copy.deepcopy(board)
            sim_piece = sim_board.squares[row][col].piece
            sim_board.move(sim_piece, move)
            if sim_board.has_pending_promotion():
                sim_board.promote_pawn('q')

            score = self._score_position(sim_board)

            if best_choice is None:
                best_score = score
                best_choice = (piece, move)
                continue

            if self.color == 'white' and score > best_score:
                best_score = score
                best_choice = (piece, move)
            elif self.color == 'black' and score < best_score:
                best_score = score
                best_choice = (piece, move)

        return best_choice

    def _score_position(self, board):
        total = 0.0
        for row in board.squares:
            for square in row:
                if square.has_piece():
                    total += square.piece.value

        opponent = 'black' if self.color == 'white' else 'white'
        if not board.has_any_legal_move(opponent):
            if board.is_in_check(opponent):
                return 999999 if self.color == 'white' else -999999
            return 0.0

        if board.is_in_check(opponent):
            total += 0.4 if self.color == 'white' else -0.4

        return total
