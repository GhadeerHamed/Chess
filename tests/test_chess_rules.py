import os
import sys
import unittest
import pygame

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from board import Board
from game import Game
from move import Move
from ai import AI
from piece import Bishop, King, Knight, Pawn, Queen, Rook
from square import Square


class TestChessRules(unittest.TestCase):
    def test_pawn_promotion_select_queen(self):
        board = Board()
        board._create()
        board.squares[7][4].piece = King('white')
        board.squares[0][4].piece = King('black')

        pawn = Pawn('white')
        board.squares[1][0].piece = pawn

        move = Move(Square(1, 0), Square(0, 0))
        board.move(pawn, move)

        self.assertTrue(board.has_pending_promotion())
        self.assertTrue(board.move_history[-1].endswith('=?'))
        self.assertTrue(board.promote_pawn('q'))
        self.assertFalse(board.has_pending_promotion())

        self.assertIsInstance(board.squares[0][0].piece, Queen)
        self.assertTrue(board.move_history[-1].endswith('=Q'))

    def test_en_passant_generation_and_execution(self):
        board = Board()
        board._create()
        board.squares[7][4].piece = King('white')
        board.squares[0][4].piece = King('black')

        white_pawn = Pawn('white')
        black_pawn = Pawn('black')
        black_pawn.en_passant = True

        board.squares[3][4].piece = white_pawn
        board.squares[3][5].piece = black_pawn

        board.calc_moves(white_pawn, 3, 4)
        en_passant_moves = [
            move for move in white_pawn.moves
            if move.final.row == 2 and move.final.col == 5
        ]
        self.assertEqual(len(en_passant_moves), 1)

        board.move(white_pawn, en_passant_moves[0])
        self.assertIsNone(board.squares[3][5].piece)
        self.assertIs(board.squares[2][5].piece, white_pawn)

    def test_castling_generation_and_execution(self):
        board = Board()
        board.squares[7][5].piece = None
        board.squares[7][6].piece = None

        king = board.squares[7][4].piece
        board.calc_moves(king, 7, 4)

        castle_moves = [
            move for move in king.moves
            if move.final.row == 7 and move.final.col == 6
        ]
        self.assertEqual(len(castle_moves), 1)

        board.move(king, castle_moves[0])
        self.assertIs(board.squares[7][6].piece, king)
        self.assertIsInstance(board.squares[7][5].piece, Rook)
        self.assertIsNone(board.squares[7][7].piece)
        self.assertEqual(board.move_history[-1], 'O-O')

    def test_checkmate_detection_helpers(self):
        board = Board()
        board._create()

        board.squares[0][0].piece = King('black')
        board.squares[1][1].piece = Queen('white')
        board.squares[2][2].piece = King('white')

        self.assertTrue(board.is_in_check('black'))
        self.assertFalse(board.has_any_legal_move('black'))

    def test_stalemate_detection_helpers(self):
        board = Board()
        board._create()

        board.squares[0][0].piece = King('black')
        board.squares[1][2].piece = Queen('white')
        board.squares[2][2].piece = King('white')

        self.assertFalse(board.is_in_check('black'))
        self.assertFalse(board.has_any_legal_move('black'))

    def test_pinned_piece_move_is_filtered(self):
        board = Board()
        board._create()

        board.squares[7][4].piece = King('white')
        white_rook = Rook('white')
        board.squares[6][4].piece = white_rook
        board.squares[0][4].piece = Rook('black')
        board.squares[0][0].piece = King('black')

        board.calc_moves(white_rook, 6, 4)

        illegal_sideways = [
            move for move in white_rook.moves
            if move.final.row == 6 and move.final.col == 5
        ]
        self.assertEqual(illegal_sideways, [])

    def test_insufficient_material_kings_only(self):
        board = Board()
        board._create()
        board.squares[7][4].piece = King('white')
        board.squares[0][4].piece = King('black')

        self.assertTrue(board.is_insufficient_material())

    def test_insufficient_material_bishop_same_color(self):
        board = Board()
        board._create()
        board.squares[7][4].piece = King('white')
        board.squares[0][4].piece = King('black')
        board.squares[4][4].piece = Bishop('white')
        board.squares[2][2].piece = Bishop('black')

        self.assertTrue(board.is_insufficient_material())

    def test_fifty_move_counter_advances_on_non_pawn_non_capture(self):
        board = Board()
        board._create()
        board.squares[7][4].piece = King('white')
        board.squares[0][4].piece = King('black')
        rook = Rook('white')
        board.squares[6][0].piece = rook

        move = Move(Square(6, 0), Square(5, 0))
        board.move(rook, move)

        self.assertEqual(board.halfmove_clock, 1)

    def test_threefold_repetition_draw_detection(self):
        pygame.init()
        game = Game()
        board = game.board

        board._create()
        board.squares[7][4].piece = King('white')
        board.squares[0][4].piece = King('black')
        white_knight = Knight('white')
        black_knight = Knight('black')
        board.squares[7][1].piece = white_knight
        board.squares[0][1].piece = black_knight

        game.next_player = 'white'
        game.position_counts = {}
        game._record_position()

        sequence = [
            ((7, 1), (5, 2)),
            ((0, 1), (2, 2)),
            ((5, 2), (7, 1)),
            ((2, 2), (0, 1)),
            ((7, 1), (5, 2)),
            ((0, 1), (2, 2)),
            ((5, 2), (7, 1)),
            ((2, 2), (0, 1)),
        ]

        for (fr, fc), (tr, tc) in sequence:
            piece = board.squares[fr][fc].piece
            move = Move(Square(fr, fc), Square(tr, tc))
            board.move(piece, move)
            game.next_turn()
            game.update_game_state()

        self.assertTrue(game.game_over)
        self.assertEqual(game.result_text, 'Draw - Threefold repetition')
        pygame.quit()

    def test_undo_redo_and_branching(self):
        pygame.init()
        game = Game()
        board = game.board

        pawn_e = board.squares[6][4].piece
        move_e4 = Move(Square(6, 4), Square(4, 4))
        board.move(pawn_e, move_e4)
        game.next_turn()
        game.update_game_state()
        game.record_state()

        self.assertTrue(game.can_undo())
        self.assertFalse(game.can_redo())
        self.assertIs(board.squares[4][4].piece, pawn_e)
        self.assertEqual(game.next_player, 'black')

        self.assertTrue(game.undo())
        board = game.board
        self.assertIsNone(board.squares[4][4].piece)
        self.assertEqual(board.squares[6][4].piece.name, 'pawn')
        self.assertEqual(game.next_player, 'white')
        self.assertTrue(game.can_redo())

        self.assertTrue(game.redo())
        board = game.board
        self.assertEqual(board.squares[4][4].piece.name, 'pawn')
        self.assertEqual(game.next_player, 'black')

        self.assertTrue(game.undo())
        board = game.board
        pawn_d = board.squares[6][3].piece
        move_d4 = Move(Square(6, 3), Square(4, 3))
        board.move(pawn_d, move_d4)
        game.next_turn()
        game.update_game_state()
        game.record_state()

        self.assertFalse(game.can_redo())
        self.assertEqual(game.board.squares[4][3].piece.name, 'pawn')
        pygame.quit()

    def test_ai_chooses_legal_move(self):
        board = Board()
        ai = AI('black')

        choice = ai.choose_move(board)
        self.assertIsNotNone(choice)

        piece, move = choice
        self.assertEqual(piece.color, 'black')
        self.assertTrue(board.valid_move(piece, move))

    def test_game_ai_turn_executes_move(self):
        pygame.init()
        game = Game()
        game.vs_ai = True
        game.next_player = 'black'
        surface = pygame.Surface((600, 600))

        before_moves = len(game.board.move_history)
        game.make_ai_move(surface)

        self.assertEqual(game.next_player, 'white')
        self.assertEqual(len(game.board.move_history), before_moves + 1)
        pygame.quit()

    def test_minimax_prefers_major_capture(self):
        board = Board()
        board._create()

        board.squares[7][4].piece = King('white')
        board.squares[0][4].piece = King('black')
        board.squares[4][4].piece = Queen('white')
        board.squares[3][4].piece = Queen('black')
        board.squares[2][4].piece = Pawn('black')

        ai = AI('white', algorithm='minimax', depth=2)
        piece, move = ai.choose_move(board)

        self.assertEqual(piece.color, 'white')
        self.assertEqual((move.final.row, move.final.col), (3, 4))

    def test_ai_algorithm_and_depth_controls(self):
        ai = AI('black', algorithm='minimax', depth=2)
        self.assertEqual(ai.get_algorithm(), 'minimax')
        self.assertEqual(ai.get_search_depth(), 2)

        ai.set_search_depth(3)
        self.assertEqual(ai.get_search_depth(), 3)

        ai.set_algorithm('greedy')
        self.assertEqual(ai.get_algorithm(), 'greedy')

        algorithms = ai.get_algorithms()
        self.assertIn('greedy', algorithms)
        self.assertIn('minimax', algorithms)


if __name__ == '__main__':
    unittest.main()
