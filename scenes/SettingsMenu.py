import pygame as pg
from .template import SceneTemplate


class SettingsScene(SceneTemplate):

    def __init__(self, app):
        super().__init__(app)

        self.options = tuple(app.settings.keys())
        self.index = 0
        self.optionselected = False
    

    def update(self, dt):

        if self.app.keyspressed[pg.K_ESCAPE]:
            self.app.keyspressed[pg.K_ESCAPE] = False
            self.quitScene()

        if self.app.keyspressed[pg.K_UP]:
            self.app.keyspressed[pg.K_UP] = False
            self.index = (self.index - 1) % len(self.options)

        if self.app.keyspressed[pg.K_DOWN]:
            self.app.keyspressed[pg.K_DOWN] = False
            self.index = (self.index + 1) % len(self.options)
        
        if self.app.keyspressed[pg.K_LEFT]:
            self.app.keyspressed[pg.K_LEFT] = False
            self.app.settings[self.options[self.index]] -= 1
        
        if self.app.keyspressed[pg.K_RIGHT]:
            self.app.keyspressed[pg.K_RIGHT] = False
            self.app.settings[self.options[self.index]] += 1


    def render(self, display):

        display.fill((55, 55, 55))

        titleFont = pg.font.Font(self.app.fontFile, round(64 * self.scale))
        title = titleFont.render("Settings", False, (255, 255, 255))
        offset = 20 * self.scale, 20 * self.scale
        display.blit(title, offset)

        optionFont = pg.font.Font(self.app.fontFile, round(32 * self.scale))
        for i, option in enumerate(self.options):
            color = (55, 55, 55) if self.index == i else (255, 255, 255)
            optionText = optionFont.render(option, False, color)
            optionValue = optionFont.render(str(self.app.settings[self.options[i]]), False, color)
            textOffset = 30 * self.scale, (30 * i + 90) * self.scale
            valueOffset = self.app.dim[0] - optionValue.get_width() - 20 * self.scale, (30 * i + 90) * self.scale
            if self.index == i:
                pg.draw.rect(display, (255, 255, 255), (textOffset[0] - 5 * self.scale, textOffset[1] - 5 * self.scale, self.app.dim[0] - 40 * self.scale, optionText.get_height() + 10 * self.scale))
            display.blit(optionText, textOffset)
            display.blit(optionValue, valueOffset)