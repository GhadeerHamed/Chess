import pygame
import sys
from game import Game

from const import *
from move import Move
from square import Square


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()

    def mainloop(self):
        screen = self.screen
        game = self.game
        dragger = game.dragger
        board = game.board

        while True:
            if game.game_over:
                pygame.display.set_caption(f'Chess - {game.result_text} (Press R to restart)')
            elif board.has_pending_promotion():
                pygame.display.set_caption('Chess - Promotion pending (Q/R/B/N)')
            else:
                pygame.display.set_caption(f'Chess - {game.next_player.capitalize()} to move')

            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            game.show_side_panel(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game.handle_navigation_click(event.pos):
                        dragger.undrag_piece()
                        board = game.board
                        continue

                    if board.has_pending_promotion():
                        if game.handle_promotion_click(event.pos):
                            game.next_turn()
                            game.update_game_state()
                            game.record_state(replace_current=True)
                        continue

                    dragger.update_mouse(event.pos)
                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE

                    # print(dragger.mouseY, clicked_row)
                    # print(dragger.mouseX, clicked_col)

                    # If square has a piece
                    if Square.in_range(clicked_row, clicked_col) and board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        if (not game.game_over) and (not board.has_pending_promotion()) and piece.color == game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            game.show_side_panel(screen)

                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE
                    if Square.in_range(motion_row, motion_col):
                        game.set_hover(motion_row, motion_col)
                    else:
                        game.hovered_sqr = None

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        game.show_side_panel(screen)
                        dragger.update_blit(screen)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        if Square.in_range(released_row, released_col):
                            # create possible moves
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)
                            is_en_passant_capture = (
                                dragger.piece.name == 'pawn' and
                                dragger.initial_col != released_col and
                                board.squares[released_row][released_col].isempty()
                            )
                            captured = board.squares[released_row][released_col].has_enemy_piece(dragger.piece.color) or is_en_passant_capture
                            if board.valid_move(dragger.piece, move):
                                board.move(dragger.piece, move)
                                game.play_sound(captured)
                                if not board.has_pending_promotion():
                                    game.next_turn()
                                    game.update_game_state()
                                game.record_state()
                                # show methods
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                game.show_hover(screen)
                                game.show_side_panel(screen)

                    dragger.undrag_piece()

                elif event.type == pygame.KEYDOWN:
                    if board.has_pending_promotion() and game.handle_promotion_key(event.key):
                        game.next_turn()
                        game.update_game_state()
                        continue

                    if event.key == pygame.K_t:
                        game.change_theme()
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        dragger = game.dragger
                        board = game.board

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

main = Main()
main.mainloop()
