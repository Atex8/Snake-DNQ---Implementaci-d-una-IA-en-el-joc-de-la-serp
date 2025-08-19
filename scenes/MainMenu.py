import pygame as pg
import os
from .template import SceneTemplate
from .GameScene import GameScene
from .SavesMenu import SavesScene
from .SettingsMenu import SettingsScene


class MainMenu(SceneTemplate):

    def __init__(self, app):
        super().__init__(app)

        self.menuOptions = (
            ("Play", self._play),
            ("Saves", self._saves),
            ("Settings", self._settings),
            ("Close", self.quitScene)
        )
        self.index = 0

    
    def _play(self):

        self.addScene(GameScene(self.app))


    def _saves(self):

        self.addScene(SavesScene(self.app))


    def _settings(self):

        self.addScene(SettingsScene(self.app))


    def update(self, dt):
        
        if self.app.keyspressed[pg.K_SPACE]:
            self.app.keyspressed[pg.K_SPACE] = False
            self.menuOptions[self.index][1]()

        if self.app.keyspressed[pg.K_UP]:
            self.app.keyspressed[pg.K_UP] = False
            self.index = (self.index - 1) % len(self.menuOptions)

        if self.app.keyspressed[pg.K_DOWN]:
            self.app.keyspressed[pg.K_DOWN] = False
            self.index = (self.index + 1) % len(self.menuOptions)
    

    def render(self, display):
        
        display.fill((55, 55, 55))

        titleFont = pg.font.Font(self.app.fontFile, round(64 * self.scale))
        optionsFont = pg.font.Font(self.app.fontFile, round(32 * self.scale))
        
        title = titleFont.render("Snake AI", False, (255, 255, 255))
        titleOffset = (self.app.dim[0] - title.get_width()) // 2, (self.app.dim[1] - 2 * title.get_height()) // 4
        display.blit(title, titleOffset)
        
        for i, option in enumerate(self.menuOptions):
            text = optionsFont.render(option[0], False, (255, 255, 255))
            offset = (self.app.dim[0] - text.get_width()) // 2, round((self.app.dim[1] - 2 * text.get_height()) / 4 + (32 * i + 64) * self.scale)
            display.blit(text, offset)

            if i == self.index:
                pg.draw.rect(display, (255, 255, 255), (offset[0] - 40 * self.scale, offset[1] + text.get_height() / 2 - 5 * self.scale, 10 * self.scale, 10 * self.scale))
                pg.draw.rect(display, (255, 255, 255), (offset[0] + text.get_width() + 30 * self.scale, offset[1] + text.get_height() / 2 - 5 * self.scale, 10 * self.scale, 10 * self.scale))