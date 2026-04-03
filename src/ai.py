import copy


MATE_SCORE = 1000000

PAWN_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [12, 14, 16, 22, 22, 16, 14, 12],
    [8, 10, 12, 18, 18, 12, 10, 8],
    [3, 6, 8, 14, 14, 8, 6, 3],
    [0, 2, 4, 8, 8, 4, 2, 0],
    [0, 0, 0, -8, -8, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

KNIGHT_PST = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 2, 2, 0, -20, -40],
    [-30, 2, 12, 14, 14, 12, 2, -30],
    [-30, 4, 14, 18, 18, 14, 4, -30],
    [-30, 2, 14, 18, 18, 14, 2, -30],
    [-30, 4, 10, 14, 14, 10, 4, -30],
    [-40, -20, 0, 4, 4, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

BISHOP_PST = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 6, 2, 2, 2, 2, 6, -10],
    [-10, 2, 10, 12, 12, 10, 2, -10],
    [-10, 2, 12, 14, 14, 12, 2, -10],
    [-10, 2, 10, 14, 14, 10, 2, -10],
    [-10, 8, 8, 10, 10, 8, 8, -10],
    [-10, 6, 0, 0, 0, 0, 6, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

ROOK_PST = [
    [0, 0, 2, 6, 6, 2, 0, 0],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [8, 10, 10, 10, 10, 10, 10, 8],
    [0, 0, 2, 8, 8, 2, 0, 0],
]

QUEEN_PST = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 8, 8, 8, 8, 0, -10],
    [-5, 0, 8, 8, 8, 8, 0, -5],
    [0, 0, 8, 8, 8, 8, 0, -5],
    [-10, 8, 8, 8, 8, 8, 0, -10],
    [-10, 0, 8, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]

KING_PST = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

PST_BY_PIECE = {
    'pawn': PAWN_PST,
    'knight': KNIGHT_PST,
    'bishop': BISHOP_PST,
    'rook': ROOK_PST,
    'queen': QUEEN_PST,
    'king': KING_PST,
}


class AIStrategy:
    name = "base"

    def choose(self, ai, board):
        raise NotImplementedError


class GreedyStrategy(AIStrategy):
    name = "greedy"

    def choose(self, ai, board):
        candidates = board.get_all_legal_moves(ai.color)
        if not candidates:
            ai.last_analysis = {
                "algorithm": self.name,
                "depth": 1,
                "nodes": 0,
                "score_cp_ai": 0,
                "score_cp_white": 0,
            }
            return None

        best_score = None
        best_choice = None
        nodes = 0

        for piece, move, row, col in candidates:
            sim_board = ai._simulate_move(board, row, col, move)
            score_ai = ai._evaluate_ai_cp(sim_board)
            nodes += 1

            if best_choice is None or score_ai > best_score:
                best_score = score_ai
                best_choice = (piece, move)

        ai._store_analysis(self.name, 1, nodes, best_score)
        return best_choice


class MinimaxStrategy(AIStrategy):
    name = "minimax"

    def __init__(self, depth=2):
        self.depth = depth
        self.tt = {}
        self.nodes = 0

    def choose(self, ai, board):
        self.nodes = 0
        if len(self.tt) > 200000:
            self.tt.clear()

        candidates = board.get_all_legal_moves(ai.color)
        if not candidates:
            ai.last_analysis = {
                "algorithm": self.name,
                "depth": self.depth,
                "nodes": 0,
                "score_cp_ai": -MATE_SCORE,
                "score_cp_white": -MATE_SCORE if ai.color == "white" else MATE_SCORE,
                "mate_for_white": None,
            }
            return None

        ordered = sorted(
            candidates,
            key=lambda item: ai._move_order_key(board, item),
            reverse=True,
        )

        best_score = -float("inf")
        best_choice = None
        alpha = -float("inf")
        beta = float("inf")
        opponent = ai._opponent(ai.color)

        for piece, move, row, col in ordered:
            sim_board = ai._simulate_move(board, row, col, move)
            score = self._alphabeta(
                ai,
                sim_board,
                opponent,
                self.depth - 1,
                alpha,
                beta,
                ply=1,
            )

            if best_choice is None or score > best_score:
                best_score = score
                best_choice = (piece, move)

            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        ai._store_analysis(self.name, self.depth, self.nodes, int(best_score))
        return best_choice

    def _alphabeta(self, ai, board, side_to_move, depth, alpha, beta, ply):
        self.nodes += 1

        alpha_orig = alpha
        beta_orig = beta
        tt_key = f"{board.get_position_key(side_to_move)}|d{depth}|ab"
        tt_entry = self.tt.get(tt_key)
        if tt_entry and tt_entry["depth"] >= depth:
            if tt_entry["flag"] == "exact":
                return tt_entry["score"]
            if tt_entry["flag"] == "lower":
                alpha = max(alpha, tt_entry["score"])
            elif tt_entry["flag"] == "upper":
                beta = min(beta, tt_entry["score"])
            if alpha >= beta:
                return tt_entry["score"]

        legal_moves = board.get_all_legal_moves(side_to_move)
        if not legal_moves:
            if board.is_in_check(side_to_move):
                mate_value = MATE_SCORE - ply
                if side_to_move == ai.color:
                    return -mate_value
                return mate_value
            return 0

        if board.halfmove_clock >= 100 or board.is_insufficient_material():
            return 0

        if depth <= 0:
            return self._quiescence(ai, board, side_to_move, alpha, beta, ply)

        ordered = sorted(
            legal_moves,
            key=lambda item: ai._move_order_key(board, item),
            reverse=True,
        )

        if side_to_move == ai.color:
            best = -float("inf")
            for _, move, row, col in ordered:
                sim_board = ai._simulate_move(board, row, col, move)
                child = self._alphabeta(
                    ai,
                    sim_board,
                    ai._opponent(side_to_move),
                    depth - 1,
                    alpha,
                    beta,
                    ply + 1,
                )
                best = max(best, child)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            score = int(best)
        else:
            best = float("inf")
            for _, move, row, col in ordered:
                sim_board = ai._simulate_move(board, row, col, move)
                child = self._alphabeta(
                    ai,
                    sim_board,
                    ai._opponent(side_to_move),
                    depth - 1,
                    alpha,
                    beta,
                    ply + 1,
                )
                best = min(best, child)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            score = int(best)

        if score <= alpha_orig:
            flag = "upper"
        elif score >= beta_orig:
            flag = "lower"
        else:
            flag = "exact"

        self.tt[tt_key] = {"depth": depth, "score": score, "flag": flag}
        return score

    def _quiescence(self, ai, board, side_to_move, alpha, beta, ply):
        self.nodes += 1

        stand_pat = ai._evaluate_ai_cp(board)
        if side_to_move != ai.color:
            stand_pat = ai._evaluate_ai_cp(board)

        if side_to_move == ai.color:
            if stand_pat >= beta:
                return stand_pat
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return stand_pat
            beta = min(beta, stand_pat)

        moves = board.get_all_legal_moves(side_to_move)
        capture_moves = [m for m in moves if ai._is_capture_move(board, m)]
        ordered = sorted(capture_moves, key=lambda item: ai._move_order_key(board, item), reverse=True)

        if not ordered:
            return stand_pat

        if side_to_move == ai.color:
            best = stand_pat
            for _, move, row, col in ordered:
                sim_board = ai._simulate_move(board, row, col, move)
                score = self._quiescence(ai, sim_board, ai._opponent(side_to_move), alpha, beta, ply + 1)
                best = max(best, score)
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
            return int(best)

        best = stand_pat
        for _, move, row, col in ordered:
            sim_board = ai._simulate_move(board, row, col, move)
            score = self._quiescence(ai, sim_board, ai._opponent(side_to_move), alpha, beta, ply + 1)
            best = min(best, score)
            beta = min(beta, best)
            if alpha >= beta:
                break
        return int(best)


class AI:
    def __init__(self, color="black", algorithm="minimax", depth=2):
        self.color = color
        self.algorithms = {}
        self.last_analysis = {
            "algorithm": "minimax",
            "depth": depth,
            "nodes": 0,
            "score_cp_ai": 0,
            "score_cp_white": 0,
            "mate_for_white": None,
        }

        self.register_algorithm("greedy", GreedyStrategy())
        self.register_algorithm("minimax", MinimaxStrategy(depth=depth))
        self.set_algorithm(algorithm)

    def register_algorithm(self, name, strategy):
        self.algorithms[name] = strategy

    def set_algorithm(self, name):
        if name not in self.algorithms:
            raise ValueError(f"Unknown AI algorithm: {name}")
        self.algorithm = name

    def get_algorithm(self):
        return self.algorithm

    def get_algorithms(self):
        return list(self.algorithms.keys())

    def set_search_depth(self, depth):
        if "minimax" in self.algorithms and hasattr(self.algorithms["minimax"], "depth"):
            self.algorithms["minimax"].depth = max(1, int(depth))

    def get_search_depth(self):
        minimax = self.algorithms.get("minimax")
        if minimax and hasattr(minimax, "depth"):
            return minimax.depth
        return 1

    def get_last_analysis(self):
        return dict(self.last_analysis)

    def choose_move(self, board):
        strategy = self.algorithms[self.algorithm]
        return strategy.choose(self, board)

    def choose_move_descriptor(self, board):
        choice = self.choose_move(board)
        if not choice:
            return None

        piece, move = choice
        return {
            "piece_name": piece.name,
            "piece_color": piece.color,
            "from_row": move.initial.row,
            "from_col": move.initial.col,
            "to_row": move.final.row,
            "to_col": move.final.col,
        }

    def _opponent(self, color):
        return "black" if color == "white" else "white"

    def _simulate_move(self, board, row, col, move):
        sim_board = copy.deepcopy(board)
        sim_piece = sim_board.squares[row][col].piece
        sim_board.move(sim_piece, move)
        if sim_board.has_pending_promotion():
            sim_board.promote_pawn("q")
        return sim_board

    def _move_order_key(self, board, item):
        piece, move, _, _ = item
        score = 0

        target = board.squares[move.final.row][move.final.col].piece
        if target is not None:
            score += int(abs(target.value) * 100)

        if piece.name == "pawn" and (move.final.row == 0 or move.final.row == 7):
            score += 800

        center_bonus = 3 - abs(3.5 - move.final.row) + 3 - abs(3.5 - move.final.col)
        score += int(center_bonus * 5)
        return score

    def _is_capture_move(self, board, item):
        piece, move, _, _ = item
        target = board.squares[move.final.row][move.final.col]
        if target.has_enemy_piece(piece.color):
            return True

        if piece.name == "pawn" and move.initial.col != move.final.col and target.isempty():
            return True

        return False

    def _store_analysis(self, algorithm, depth, nodes, score_cp_ai):
        score_cp_white = score_cp_ai if self.color == "white" else -score_cp_ai
        mate_for_white = self._mate_for_white_from_score(score_cp_white)
        self.last_analysis = {
            "algorithm": algorithm,
            "depth": depth,
            "nodes": nodes,
            "score_cp_ai": int(score_cp_ai),
            "score_cp_white": int(score_cp_white),
            "mate_for_white": mate_for_white,
        }

    def _mate_for_white_from_score(self, score_cp_white):
        if abs(score_cp_white) < MATE_SCORE - 2000:
            return None

        plies_to_mate = MATE_SCORE - abs(score_cp_white)
        moves_to_mate = max(1, (plies_to_mate + 1) // 2)
        return moves_to_mate if score_cp_white > 0 else -moves_to_mate

    def _evaluate_ai_cp(self, board):
        return self._evaluate_white_cp(board) if self.color == "white" else -self._evaluate_white_cp(board)

    def _evaluate_white_cp(self, board):
        material_cp = 0
        positional_cp = 0
        for row in board.squares:
            for square in row:
                if square.has_piece():
                    piece = square.piece
                    material_cp += int(piece.value * 100)

        for r in range(8):
            for c in range(8):
                square = board.squares[r][c]
                if not square.has_piece():
                    continue

                piece = square.piece
                pst = PST_BY_PIECE.get(piece.name)
                if not pst:
                    continue

                if piece.color == 'white':
                    positional_cp += pst[r][c]
                else:
                    positional_cp -= pst[7 - r][c]

        white_mob = len(board.get_all_legal_moves("white"))
        black_mob = len(board.get_all_legal_moves("black"))
        mobility_cp = 3 * (white_mob - black_mob)

        check_cp = 0
        if board.is_in_check("black"):
            check_cp += 30
        if board.is_in_check("white"):
            check_cp -= 30

        return material_cp + positional_cp + mobility_cp + check_cp