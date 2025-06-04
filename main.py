import time
import pygame as pg
from scenes.GameScene import GameScene


class App:

    def __init__(self):

        self.dim = 1280, 720
        self.display = pg.display.set_mode(self.dim, pg.RESIZABLE)
        self.stack = [GameScene(self)]


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
    

    def _update(self, dt):

        self.stack[-1].update(dt)


    def _updateUI(self):

        surface = self.stack[-1].render()
        self.display.blit(surface, (0, 0))
        pg.display.flip()


if __name__ == "__main__":

    pg.init()
    app = App()
    app.mainLoop()
    pg.quit()