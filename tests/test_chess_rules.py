import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from board import Board
from move import Move
from piece import King, Pawn, Queen, Rook
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


if __name__ == '__main__':
    unittest.main()
