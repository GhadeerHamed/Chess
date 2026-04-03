import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.game_over = False
        self.result_text = ''
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.texture_cache = {}
        self.promotion_buttons = {}

    def _get_cached_texture(self, piece, size):
        piece.set_texture(size=size)
        texture_path = piece.texture
        if texture_path not in self.texture_cache:
            self.texture_cache[texture_path] = pygame.image.load(texture_path)
        return self.texture_cache[texture_path]

    # blit methods

    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    label_color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(str(ROWS - row), 1, label_color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    label_color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, label_color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    surface.blit(lbl, lbl_pos)


    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # piece ?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    # all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        img = self._get_cached_texture(piece, 80)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:
                # color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            color = (180, 180, 180)
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect, width=3)

    def show_move_history(self, surface):
        self.show_side_panel(surface)

    def show_side_panel(self, surface):
        panel_x = BOARD_SIZE
        panel_w = SIDE_PANEL_WIDTH

        pygame.draw.rect(surface, (26, 28, 32), (panel_x, 0, panel_w, HEIGHT))
        pygame.draw.line(surface, (70, 74, 84), (panel_x, 0), (panel_x, HEIGHT), 2)

        title = self.config.font.render('Chess', True, (236, 236, 236))
        surface.blit(title, (panel_x + 14, 12))

        self._draw_status_card(surface, panel_x + 12, 44, panel_w - 24, 92)

        promo_height = 170 if self.board.has_pending_promotion() else 66
        next_y = 146
        self._draw_promotion_card(surface, panel_x + 12, next_y, panel_w - 24, promo_height)

        history_y = next_y + promo_height + 12
        history_h = HEIGHT - history_y - 12
        self._draw_history_card(surface, panel_x + 12, history_y, panel_w - 24, history_h)

    def _draw_status_card(self, surface, x, y, w, h):
        pygame.draw.rect(surface, (44, 48, 56), (x, y, w, h), border_radius=8)
        pygame.draw.rect(surface, (86, 92, 106), (x, y, w, h), width=1, border_radius=8)

        if self.game_over:
            title = 'Game Over'
            status = self.result_text
            hint = 'Press R to restart'
        elif self.board.has_pending_promotion():
            title = 'Promotion'
            status = f'{self.next_player.capitalize()} choose piece'
            hint = 'Click choice or press Q/R/B/N'
        else:
            title = 'Turn'
            status = f'{self.next_player.capitalize()} to move'
            hint = 'In check' if self.board.is_in_check(self.next_player) else 'Board active'

        title_txt = self.config.font.render(title, True, (230, 230, 230))
        status_txt = self.config.font.render(status, True, (245, 245, 245))
        hint_txt = self.config.font.render(hint, True, (198, 203, 214))
        surface.blit(title_txt, (x + 10, y + 10))
        surface.blit(status_txt, (x + 10, y + 36))
        surface.blit(hint_txt, (x + 10, y + 60))

    def _draw_history_card(self, surface, x, y, w, h):
        pygame.draw.rect(surface, (44, 48, 56), (x, y, w, h), border_radius=8)
        pygame.draw.rect(surface, (86, 92, 106), (x, y, w, h), width=1, border_radius=8)

        title = self.config.font.render('Move History', True, (230, 230, 230))
        surface.blit(title, (x + 10, y + 10))

        available_rows = max(1, (h - 36) // 18)
        visible_moves = self.board.move_history[-available_rows:]
        start_idx = max(0, len(self.board.move_history) - len(visible_moves))

        for idx, notation in enumerate(visible_moves):
            ply_number = start_idx + idx + 1
            line = f'{ply_number}. {notation}'
            text = self.config.font.render(line, True, (232, 232, 232))
            surface.blit(text, (x + 10, y + 34 + idx * 18))

    def _draw_promotion_card(self, surface, x, y, w, h):
        self.promotion_buttons = {}
        pygame.draw.rect(surface, (44, 48, 56), (x, y, w, h), border_radius=8)
        pygame.draw.rect(surface, (86, 92, 106), (x, y, w, h), width=1, border_radius=8)

        title = self.config.font.render('Promotion', True, (230, 230, 230))
        surface.blit(title, (x + 10, y + 10))

        if not self.board.has_pending_promotion():
            info = self.config.font.render('No pending promotion', True, (198, 203, 214))
            surface.blit(info, (x + 10, y + 34))
            return

        options = [('Q', 'Queen'), ('R', 'Rook'), ('B', 'Bishop'), ('N', 'Knight')]
        for idx, (code, label) in enumerate(options):
            btn_x = x + 12
            btn_y = y + 34 + idx * 31
            btn_w = w - 24
            btn_h = 26
            rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            pygame.draw.rect(surface, (205, 208, 214), rect, border_radius=5)
            pygame.draw.rect(surface, (55, 58, 66), rect, width=1, border_radius=5)
            txt = self.config.font.render(f'{code} - {label}', True, (26, 26, 26))
            surface.blit(txt, (btn_x + 8, btn_y + 4))
            self.promotion_buttons[code.lower()] = rect

    def handle_promotion_click(self, pos):
        for code, rect in self.promotion_buttons.items():
            if rect.collidepoint(pos):
                return self.board.promote_pawn(code)
        return False

    def handle_promotion_key(self, key):
        key_map = {
            pygame.K_q: 'q',
            pygame.K_r: 'r',
            pygame.K_b: 'b',
            pygame.K_n: 'n'
        }
        code = key_map.get(key)
        if not cod