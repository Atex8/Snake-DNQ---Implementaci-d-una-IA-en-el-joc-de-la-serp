import time
import pygame as pg
from scenes.GameScene import GameScene


class App:

    def __init__(self):

        self.dim = 640, 360
        self.display = pg.display.set_mode(self.dim, pg.RESIZABLE)
        self.stack = [GameScene(self)]
        self.keyspressed = {
            pg.K_SPACE: False
        }


    def mainLoop(self):

        self.running = True
        prevtime = time.time()
        while self.running:
            dt = time.time() - prevtime
            prevtime = time.time()
            self._checkInput()
            self._update(dt)
            self._updateUI()

    
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