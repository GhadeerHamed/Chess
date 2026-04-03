import pygame

from const import *

class Dragger:

    def __init__(self):
        self.piece = None
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0
        self.texture_cache = {}

    def _get_cached_texture(self, piece, size):
        piece.set_texture(size=size)
        texture_path = piece.texture
        if texture_path not in self.texture_cache:
            self.texture_cache[texture_path] = pygame.image.load(texture_path)
        return self.texture_cache[texture_path]

    # blit method

    def update_blit(self, surface):
        img = self._get_cached_texture(self.piece, 128)
        # rect
        img_center = (self.mouseX, self.mouseY)
        self.piece.texture_rect = img.get_rect(center=img_center)
        # blit
        surface.blit(img, self.piece.texture_rect)

    # other methods

    def update_mouse(self, pos):
        self.mouseX, self.mouseY = pos # (xcor, ycor)

    def save_initial(self, pos):
        self.initial_row = pos[1] // SQSIZE
        self.initial_col = pos[0] // SQSIZE

    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = None
        self.dragging = False
