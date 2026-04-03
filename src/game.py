import pygame
import copy

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
        self.position_counts = {}
        self.nav_buttons = {}
        self.state_history = []
        self.state_index = -1
        self._record_position()
        self.record_state()

    def _get_cached_texture(self, piece, size):
        piece.set_texture(size=size)
        texture_path = piece.texture
        if texture_path not in self.texture_cache:
            self.texture_cache[texture_path] = pygame.image.load(texture_path)
        return self.texture_cache[texture_path]

    def _fit_text(self, text, max_width):
        if self.config.font.size(text)[0] <= max_width:
            return text

        suffix = '...'
        fitted = text
        while fitted and self.config.font.size(fitted + suffix)[0] > max_width:
            fitted = fitted[:-1]

        return (fitted + suffix) if fitted else suffix

    def _wrap_text(self, text, max_width, max_lines):
        words = text.split()
        if not words:
            return ['']

        lines = []
        current = words[0]

        for word in words[1:]:
            trial = f'{current} {word}'
            if self.config.font.size(trial)[0] <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word

        lines.append(current)

        if len(lines) <= max_lines:
            return lines

        clipped = lines[:max_lines]
        clipped[-1] = self._fit_text(clipped[-1], max_width)
        return clipped

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

        nav_y = 146
        self._draw_navigation_card(surface, panel_x + 12, nav_y, panel_w - 24, 56)

        promo_height = 170 if self.board.has_pending_promotion() else 66
        next_y = nav_y + 66
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
        status_lines = self._wrap_text(status, w - 20, 2)
        hint_line = self._fit_text(hint, w - 20)
        surface.blit(title_txt, (x + 10, y + 10))

        for idx, line in enumerate(status_lines):
            status_txt = self.config.font.render(line, True, (245, 245, 245))
            surface.blit(status_txt, (x + 10, y + 36 + idx * 18))

        hint_y = y + 36 + len(status_lines) * 18
        hint_txt = self.config.font.render(hint_line, True, (198, 203, 214))
        surface.blit(hint_txt, (x + 10, hint_y))

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
            line = self._fit_text(f'{ply_number}. {notation}', w - 20)
            text = self.config.font.render(line, True, (232, 232, 232))
            surface.blit(text, (x + 10, y + 34 + idx * 18))

    def _draw_promotion_card(self, surface, x, y, w, h):
        self.promotion_buttons = {}
        pygame.draw.rect(surface, (44, 48, 56), (x, y, w, h), border_radius=8)
        pygame.draw.rect(surface, (86, 92, 106), (x, y, w, h), width=1, border_radius=8)

        title = self.config.font.render('Promotion', True, (230, 230, 230))
        surface.blit(title, (x + 10, y + 10))

        if not self.board.has_pending_promotion():
            info_text = self._fit_text('No pending promotion', w - 20)
            info = self.config.font.render(info_text, True, (198, 203, 214))
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
            btn_text = self._fit_text(f'{code} - {label}', btn_w - 14)
            txt = self.config.font.render(btn_text, True, (26, 26, 26))
            surface.blit(txt, (btn_x + 8, btn_y + 4))
            self.promotion_buttons[code.lower()] = rect

    def _draw_navigation_card(self, surface, x, y, w, h):
        self.nav_buttons = {}

        pygame.draw.rect(surface, (44, 48, 56), (x, y, w, h), border_radius=8)
        pygame.draw.rect(surface, (86, 92, 106), (x, y, w, h), width=1, border_radius=8)

        gap = 8
        btn_w = (w - 30 - gap) // 2
        btn_h = 28
        btn_y = y + 14
        undo_rect = pygame.Rect(x + 10, btn_y, btn_w, btn_h)
        redo_rect = pygame.Rect(x + 20 + btn_w, btn_y, btn_w, btn_h)

        undo_enabled = self.can_undo()
        redo_enabled = self.can_redo()

        self._draw_nav_button(surface, undo_rect, 'Undo', undo_enabled)
        self._draw_nav_button(surface, redo_rect, 'Redo', redo_enabled)

        self.nav_buttons['undo'] = undo_rect if undo_enabled else None
        self.nav_buttons['redo'] = redo_rect if redo_enabled else None

    def _draw_nav_button(self, surface, rect, label, enabled):
        fill = (204, 208, 215) if enabled else (118, 122, 130)
        border = (54, 58, 66)
        text_color = (20, 20, 20) if enabled else (72, 74, 80)

        pygame.draw.rect(surface, fill, rect, border_radius=5)
        pygame.draw.rect(surface, border, rect, width=1, border_radius=5)

        label_text = self._fit_text(label, rect.width - 12)
        txt = self.config.font.render(label_text, True, text_color)
        txt_rect = txt.get_rect(center=rect.center)
        surface.blit(txt, txt_rect)

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
        if not code:
            return False
        return self.board.promote_pawn(code)

    def handle_navigation_click(self, pos):
        undo_rect = self.nav_buttons.get('undo')
        redo_rect = self.nav_buttons.get('redo')

        if undo_rect and undo_rect.collidepoint(pos):
            return self.undo()

        if redo_rect and redo_rect.collidepoint(pos):
            return self.redo()

        return False

    # other methods

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def update_game_state(self):
        self._record_position()

        in_check = self.board.is_in_check(self.next_player)
        has_moves = self.board.has_any_legal_move(self.next_player)

        if not has_moves:
            self.game_over = True
            if in_check:
                winner = 'white' if self.next_player == 'black' else 'black'
                self.result_text = f'Checkmate - {winner.capitalize()} wins'
            else:
                self.result_text = 'Draw - Stalemate'
            return

        if self.board.halfmove_clock >= 100:
            self.game_over = True
            self.result_text = 'Draw - Fifty-move rule'
            return

        if self._current_position_repetition() >= 3:
            self.game_over = True
            self.result_text = 'Draw - Threefold repetition'
            return

        if self.board.is_insufficient_material():
            self.game_over = True
            self.result_text = 'Draw - Insufficient material'
            return

        self.game_over = False
        self.result_text = ''

    def _record_position(self):
        if self.board.has_pending_promotion():
            return

        key = self.board.get_position_key(self.next_player)
        self.position_counts[key] = self.position_counts.get(key, 0) + 1

    def _current_position_repetition(self):
        key = self.board.get_position_key(self.next_player)
        return self.position_counts.get(key, 0)

    def _snapshot(self):
        return {
            'board': copy.deepcopy(self.board),
            'next_player': self.next_player,
            'game_over': self.game_over,
            'result_text': self.result_text,
            'position_counts': dict(self.position_counts),
        }

    def _restore_snapshot(self, snapshot):
        self.board = copy.deepcopy(snapshot['board'])
        self.next_player = snapshot['next_player']
        self.game_over = snapshot['game_over']
        self.result_text = snapshot['result_text']
        self.position_counts = dict(snapshot['position_counts'])
        self.hovered_sqr = None

    def record_state(self, replace_current=False):
        snapshot = self._snapshot()

        if replace_current and self.state_index >= 0:
            self.state_history[self.state_index] = snapshot
            self.state_history = self.state_history[:self.state_index + 1]
            return

        if self.state_index < len(self.state_history) - 1:
            self.state_history = self.state_history[:self.state_index + 1]

        self.state_history.append(snapshot)
        self.state_index = len(self.state_history) - 1

    def can_undo(self):
        return self.state_index > 0

    def can_redo(self):
        return self.state_index < len(self.state_history) - 1

    def undo(self):
        if not self.can_undo():
            return False

        self.state_index -= 1
        self._restore_snapshot(self.state_history[self.state_index])
        return True

    def redo(self):
        if not self.can_redo():
            return False

        self.state_index += 1
        self._restore_snapshot(self.state_history[self.state_index])
        return True

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()