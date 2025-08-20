import pygame as pg
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
from random import randint
from .template import SceneTemplate
from .AI.Agent import Agent


class GameScene(SceneTemplate):

    def __init__(self, app):
        super().__init__(app, True)

        if app.saveFile:
            with open(app.saveFile, "r") as file:
                data = json.load(file)
        
            self.width, self.height = data["width"], data["height"]

            self.agent = Agent(
                data["policyWeights"],
                data["policyBiases"],
                data["targetWeights"],
                data["targetBiases"]
            )

        else:
            self.width, self.height = app.settings["Grid width"], app.settings["Grid height"]

            self.agent = Agent()

        self.border = 20
        self.tilesize = 40
        self.dim = self.width * self.tilesize + 2 * self.border, self.height * self.tilesize + 2 * self.border
        self.screen = pg.Surface(self.dim)
        self.rel = self.dim[0] / self.dim[1]
        self.resize(app.dim)

        self.lapse = 1 / app.settings["Simulation speed (ticks/s)"]
        self.gameOverTime = 1
        self.paused = True

        self.scores = []
        self.mean_scores = []

        self._reset()
    

    def resize(self, size):
        
        if size[0] / size[1] > self.rel:
            self.scale = (size[1] * self.app.defaultDim[1]) / (self.dim[1] * self.app.defaultDim[1])
        else:
            self.scale = (size[0] * self.app.defaultDim[0]) / (self.dim[0] * self.app.defaultDim[0])


    def _reset(self):

        self.score = 0

        self.state = 0
        self.timesum = 0
        self.wastedsteps = 0

        self.head = (self.width - 1) // 2, (self.height - 1) // 2
        self.direction = 0, 1, 0, 0                                 # UP, RIGHT, DOWN, LEFT
        self.body = []
        self._placeFood()


    def _placeFood(self):
        
        self.food = randint(0, self.width - 1), randint(0, self.height - 1)
        if self.food in self.body or self.food == self.head:
            self._placeFood()
    

    def update(self, dt):
        
        if self.app.keyspressed[pg.K_SPACE]:
            self.app.keyspressed[pg.K_SPACE] = False
            self.paused = not self.paused
            self.timesum = 0
            if self.paused:
                plt.ion()
                fig, ax = plt.subplots()
                ax.plot(range(len(self.scores)), self.scores, "-o")
                ax.plot(range(len(self.mean_scores)), self.mean_scores, "-o")
                while plt.fignum_exists(fig.number):
                    plt.pause(0.01)
                plt.ioff()
        
        if self.app.keyspressed[pg.K_ESCAPE]:
            self.app.keyspressed[pg.K_ESCAPE] = False
            self.quitScene()

        if self.paused:
            if self.app.keyspressed[pg.K_UP]:
                self.app.keyspressed[pg.K_UP] = False
                self._saveData()
        else:
            self.timesum += dt
            if self.state == 0:
                if self.timesum >= self.lapse:
                    self.timesum -= self.lapse
                    self._gameStep()
            elif self.state == 1:
                if self.timesum >= self.gameOverTime:
                    self.timesum -= self.gameOverTime
                    self._reset()
    

    def _saveData(self):

        data = {
            "width": self.width,
            "height": self.height,
            "policyWeights": self.agent.policyNet.weights,
            "policyBiases": self.agent.policyNet.biases,
            "targetWeights": self.agent.targetNet.weights,
            "targetBiases": self.agent.targetNet.biases
        }
        if self.app.saveFile:
            saveFile = self.app.saveFile
        else:
            now = datetime.now()
            saveFile = os.path.join(self.app.savesFolder, f"{now.strftime("%d-%m-%Y_%H-%M-%S")}.json")
        with open(saveFile, "w") as file:
            json.dump(data, file, indent = 4)
    

    def _gameStep(self):

        state = self._getGameState()
        action = self.agent.chooseAction(state)
        self.direction = self._updateDirection(action)
        reward, done = self._playGameStep()
        nextstate = self._getGameState()
        self.agent.memory.remember(state, action, reward, nextstate, done)
        if self.state == 1:
            self.agent.train_long()
            self.agent.sync()
            self.agent.epsilon -= 1
            self.scores.append(self.score)
            self.mean_scores.append(sum(self.scores) / len(self.scores))
    

    def _getGameState(self):

        return (
            1 if self.direction[0] else 0,
            1 if self.direction[1] else 0,
            1 if self.direction[2] else 0,
            1 if self.direction[3] else 0,
            
            1 if (self.direction[0] and self._isCollision((self.head[0] - 1, self.head[1]))) or
                 (self.direction[1] and self._isCollision((self.head[0], self.head[1] - 1))) or
                 (self.direction[2] and self._isCollision((self.head[0] + 1, self.head[1]))) or
                 (self.direction[3] and self._isCollision((self.head[0], self.head[1] + 1))) else 0,
            1 if (self.direction[0] and self._isCollision((self.head[0], self.head[1] - 1))) or
                 (self.direction[1] and self._isCollision((self.head[0] + 1, self.head[1]))) or
                 (self.direction[2] and self._isCollision((self.head[0], self.head[1] + 1))) or
                 (self.direction[3] and self._isCollision((self.head[0] - 1, self.head[1]))) else 0,
            1 if (self.direction[0] and self._isCollision((self.head[0] + 1, self.head[1]))) or
                 (self.direction[1] and self._isCollision((self.head[0], self.head[1] + 1))) or
                 (self.direction[2] and self._isCollision((self.head[0] - 1, self.head[1]))) or
                 (self.direction[3] and self._isCollision((self.head[0], self.head[1] - 1))) else 0,
            
            1 if (self.direction[0] and self.food[0] < self.head[0]) or
                 (self.direction[1] and self.food[1] < self.head[1]) or
                 (self.direction[2] and self.food[0] > self.head[0]) or
                 (self.direction[3] and self.food[1] > self.head[1]) else 0,
            1 if (self.direction[0] and self.food[1] < self.head[1]) or
                 (self.direction[1] and self.food[0] > self.head[0]) or
                 (self.direction[2] and self.food[1] > self.head[1]) or
                 (self.direction[3] and self.food[0] < self.head[0]) else 0,
            1 if (self.direction[0] and self.food[0] > self.head[0]) or
                 (self.direction[1] and self.food[1] > self.head[1]) or
                 (self.direction[2] and self.food[0] < self.head[0]) or
                 (self.direction[3] and self.food[1] < self.head[1]) else 0,
            1 if (self.direction[0] and self.food[1] > self.head[1]) or
                 (self.direction[1] and self.food[0] < self.head[0]) or
                 (self.direction[2] and self.food[1] < self.head[1]) or
                 (self.direction[3] and self.food[0] > self.head[0]) else 0
        )


    def _updateDirection(self, action):

        if action[0]:
            return self.direction[1], self.direction[2], self.direction[3], self.direction[0]
        if action[2]:
            return self.direction[3], self.direction[0], self.direction[1], self.direction[2]
        return self.direction


    def _playGameStep(self):

        newHead = self.head[0] + self.direction[1] - self.direction[3], self.head[1] - self.direction[0] + self.direction[2]
        if self._isCollision(newHead) or self.wastedsteps >= 100:
            self.state += 1
            return -2, True
        elif newHead == self.food:
            self.score += 1
            self.wastedsteps = 0
            self.body.append(self.head)
            self.head = newHead
            self._placeFood()
            return 10, False
        else:
            self.wastedsteps += 1
            self.body.append(self.head)
            self.body.pop(0)
            self.head = newHead
            return -.1, False
    

    def _isCollision(self, point):

        if point[0] < 0 or point[1] < 0 or point[0] >= self.width or point[1] >= self.height or point in self.body[1:]:
            return True
        return False
    

    def render(self, display):

        self.screen.fill((55, 55, 55))
        for part in self.body:
            pg.draw.rect(self.screen, (0, 0, 255), (self.border + part[0] * self.tilesize, self.border + part[1] * self.tilesize, self.tilesize, self.tilesize))
        if self.state == 1:
            pg.draw.rect(self.screen, (255, 255, 0), (self.border + self.head[0] * self.tilesize, self.border + self.head[1] * self.tilesize, self.tilesize, self.tilesize))
        else:
            pg.draw.rect(self.screen, (0, 255, 0), (self.border + self.head[0] * self.tilesize, self.border + self.head[1] * self.tilesize, self.tilesize, self.tilesize))
        pg.draw.rect(self.screen, (255, 0, 0), (self.border + self.food[0] * self.tilesize, self.border + self.food[1] * self.tilesize, self.tilesize, self.tilesize))
        for x in range(self.width + 1):
            pg.draw.line(self.screen, (255, 255, 255), (self.border + x * self.tilesize, self.border), (self.border + x * self.tilesize, self.border + self.height * self.tilesize))
        for y in range(self.height + 1):
            pg.draw.line(self.screen, (255, 255, 255), (self.border, self.border + y * self.tilesize), (self.border + self.width * self.tilesize, self.border + y * self.tilesize))

        display.fill((55, 55, 55))
        scsurface = pg.transform.smoothscale_by(self.screen, self.scale)
        offset = (self.app.dim[0] - scsurface.get_width()) / 2, (self.app.dim[1] - scsurface.get_height()) / 2
        display.blit(scsurface, offset)