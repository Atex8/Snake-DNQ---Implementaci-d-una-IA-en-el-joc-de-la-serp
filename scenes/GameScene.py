import pygame as pg
from .template import SceneTemplate


class GameScene(SceneTemplate):

    def __init__(self, app):
        super().__init__(app)

        self.border = 10
        self.tilesize = 20
        self.width, self.height = 10, 10
        self.dim = [self.width * self.tilesize + 2 * self.border, self.height * self.tilesize + 2 * self.border]
        self.screen = pg.Surface(self.dim)
    

    def render(self):

        self.screen.fill((55, 55, 55))
        return self.screen