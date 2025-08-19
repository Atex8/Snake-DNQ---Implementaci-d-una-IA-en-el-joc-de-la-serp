import pygame as pg
import os
from .template import SceneTemplate


class SavesScene(SceneTemplate):

    def __init__(self, app):
        super().__init__(app)

        self.saves = ["New Save"]
        for file in os.listdir(app.savesFolder):
            if file.endswith(".json"):
                self.saves.append(file)
        
        self.index = 0
        self.selectedSave = self.saves.index(os.path.basename(app.saveFile)) if app.saveFile else 0


    def update(self, dt):

        if self.app.keyspressed[pg.K_ESCAPE]:
            self.app.keyspressed[pg.K_ESCAPE] = False
            if self.selectedSave:
                self.app.saveFile = os.path.join(self.app.savesFolder, self.saves[self.selectedSave])
            else:
                self.app.saveFile = None
            self.quitScene()
        
        if self.app.keyspressed[pg.K_SPACE]:
            self.app.keyspressed[pg.K_SPACE] = False
            self.selectedSave = self.index
        
        if self.app.keyspressed[pg.K_UP]:
            self.app.keyspressed[pg.K_UP] = False
            self.index = (self.index - 1) % len(self.saves)
        
        if self.app.keyspressed[pg.K_DOWN]:
            self.app.keyspressed[pg.K_DOWN] = False
            self.index = (self.index + 1) % len(self.saves)


    def render(self, display):

        display.fill((55, 55, 55))

        titleFont = pg.font.Font(self.app.fontFile, round(64 * self.scale))
        title = titleFont.render("Saves", False, (255, 255, 255))
        offset = 20 * self.scale, 20 * self.scale
        display.blit(title, offset)

        optionFont = pg.font.Font(self.app.fontFile, round(32 * self.scale))
        for i, option in enumerate(self.saves):
            color = (55, 55, 55) if self.index == i else (255, 255, 255)
            optionText = optionFont.render(option, False, color)
            textOffset = 30 * self.scale, (30 * i + 90) * self.scale
            if self.index == i:
                pg.draw.rect(display, (255, 255, 255), (textOffset[0] - 5 * self.scale, textOffset[1] - 5 * self.scale, self.app.dim[0] - 40 * self.scale, optionText.get_height() + 10 * self.scale))
            display.blit(optionText, textOffset)

            if self.selectedSave == i:
                selectedText = optionFont.render("Selected", False, color)
                selectedOffset = self.app.dim[0] - selectedText.get_width() - 20 * self.scale, (30 * i + 90) * self.scale
                display.blit(selectedText, selectedOffset)