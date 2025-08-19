import time
import pygame as pg
import os
from scenes.MainMenu import MainMenu


class App:

    def __init__(self):

        self.settings = {
            "Grid width": 10,
            "Grid height": 10,
            "Simulation speed (ticks/s)": 4
        }
        self.directory = os.path.dirname(__file__)
        self.fontFile = os.path.join(self.directory, "sources", "ByteBounce.ttf")
        self.savesFolder = os.path.join(self.directory, "saves")
        self.saveFile = None
        self.defaultDim = 640, 360
        self.dim = self.defaultDim
        self.display = pg.display.set_mode(self.dim, pg.RESIZABLE)
        self.stack = [MainMenu(self)]
        self.keyspressed = {
            pg.K_SPACE: False,
            pg.K_ESCAPE: False,
            pg.K_UP: False,
            pg.K_DOWN: False,
            pg.K_LEFT: False,
            pg.K_RIGHT: False
        }


    def mainLoop(self):

        self.running = True
        prevtime = time.time()
        while self.running:
            dt = time.time() - prevtime
            prevtime = time.time()
            self._checkInput()
            self._update(dt)
            if len(self.stack) > 0:
                self._updateUI()
            else:
                self.running = False

    
    def _checkInput(self):

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.VIDEORESIZE:
                self.dim = event.size
                for scene in self.stack:
                    scene.resize(event.size)
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                for key in self.keyspressed.keys():
                    if key == event.key:
                        self.keyspressed[key] = event.type == pg.KEYDOWN
    

    def _update(self, dt):

        self.stack[-1].update(dt)


    def _updateUI(self):

        self.stack[-1].render(self.display)
        pg.display.flip()


if __name__ == "__main__":

    pg.init()
    app = App()
    app.mainLoop()
    pg.quit()