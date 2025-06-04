import pygame as pg
from time import time
from random import randint, random, sample
from copy import deepcopy


def argMax(vals):

    return vals.index(max(vals))


class ReplayBuffer:

    def __init__(self, maxlen):

        self.memory = []
        self.maxlen = maxlen


    def remember(self, prevstate, action, reward, newstate, done):

        self.memory.append((prevstate, action, reward, newstate, done))
        if len(self.memory) > self.maxlen:
            self.memory.pop(0)


class DQN:

    def __init__(self, dim, weights = None, biases = None):
        
        self.dim = dim
        self.weights = deepcopy(weights) if weights else [[[2 * random() - 1 for k in range(self.dim[l])] for j in range(self.dim[l + 1])] for l in range(len(self.dim) - 1)]
        self.biases = deepcopy(biases) if biases else [[2 * random() - 1 for j in range(self.dim[l + 1])] for l in range(len(self.dim) - 1)]
        self.e = 2.7182818284
        self.lr = .001
    

    def forwardProp(self, inputl):

        zs = [inputl]
        activations = [[zs[0][k] for k in range(self.dim[0])]]
        for l in range(len(self.dim) - 1):
            lz = []
            la = []
            for j in range(self.dim[l + 1]):
                z = self.biases[l][j]
                for k in range(self.dim[l]):
                    z += self.weights[l][j][k] * activations[-1][k]
                lz.append(z)
                if l == len(self.dim) - 2:
                    la.append(z)
                else:
                    la.append(self.sigmoid(z))
            zs.append(lz)
            activations.append(la)
        return zs, activations
    

    def backProp(self, dloss, zs, activations):

        dz = dloss

        for l in range(len(self.dim) - 2, -1, -1):
            newdz = [0] * self.dim[l]
            for j in range(self.dim[l + 1]):
                for k in range(self.dim[l]):
                    newdz[k] += self.weights[l][j][k] * dz[j]
                    self.weights[l][j][k] -= self.lr * dz[j] * activations[l][k]
                self.biases[l][j] -= self.lr * dz[j]
            dz = [newdz[k] * self.dsigmoid(zs[l][k]) for k in range(self.dim[l])]
    

    def sigmoid(self, z):

        return 1 / (1 + self.e ** (-z))
    

    def dsigmoid(self, z):

        return self.e ** (-z) / (1 + self.e ** (-z)) ** 2


class Agent:

    def __init__(self, env):

        self.env = env

        self.epsilon = 80
        self.gamma = .1
        self.batchsize = 1000
        self.dim = 11, 20, 20, 3

        self.memory = ReplayBuffer(100000)
        self.policy = DQN(self.dim)
        self.sync()
    

    def sync(self):

        self.target = DQN(self.dim, self.policy.weights, self.policy.biases)
    

    def getAction(self, state):

        action = [0, 0, 0]
        if randint(0, 100) <= self.epsilon:
            arg = randint(0, 2)
        else:
            Qval = self.policy.forwardProp(state)[1][-1]
            arg = argMax(Qval)
        action[arg] = 1
        return tuple(action)


    def train(self, prevstate, action, reward, newstate, done):

        for i in range(len(done)):
            zs, activations = self.policy.forwardProp(prevstate[i])
            Qval = activations[-1]
            target = deepcopy(Qval)
            target[argMax(action[i])] = reward[i] if done[i] else reward[i] + self.gamma * max(self.target.forwardProp(newstate[i])[1][-1])
            dloss = [2 * (Qval[_] - target[_]) for _ in range(self.dim[-1])]
            self.policy.backProp(dloss, zs, activations)


    def trainLong(self):

        minibatch = sample(self.memory.memory, self.batchsize) if len(self.memory.memory) >= self.batchsize else self.memory.memory
        prevstate, action, reward, newstate, done = zip(*minibatch)
        self.train(prevstate, action, reward, newstate, done)


class Env:

    def __init__(self):

        self.border = 10
        self.tilesize = 20
        self.w, self.h = 10, 10
        self.dimx, self.dimy = 2 * self.border + self.w * self.tilesize, 2 * self.border + self.h * self.tilesize
        self.screen = pg.Surface((self.dimy, self.dimx), pg.SRCALPHA)
        self.ratio = self.dimx / self.dimy
        self._resizeDisplay((640, 360))
        self.window = pg.display.set_mode((self.winx, self.winy), pg.RESIZABLE)

        self.paused = True
        self.speed = .05
        self.highscore = 0
        self.ngames = 0
        self.pressedkeys = {
            pg.K_SPACE: False
        }

        self.agent = Agent(self)

        self._reset()
    

    def _resizeDisplay(self, size):

        self.winx, self.winy = size
        if size[0] / size[1] < self.ratio:
            self.scx = self.winx
            self.scy = self.winx / self.ratio
        else:
            self.scx = self.winy * self.ratio
            self.scy = self.winy
    

    def _reset(self):

        self.timesum = 0
        self.envstate = 0
        self.score = 0
        self.ngames += 1
        print(self.ngames)
        
        self.direction = 1, 0
        self.wastedsteps = 0
        self.head = self.w // 2 - 1, self.h // 2 - 1
        self.body = []
        self._placeFood()
    

    def _placeFood(self):

        self.food = randint(0, self.w - 1), randint(0, self.h - 1)
        if self.food in self.body or self.food == self.head:
            self._placeFood()


    def mainLoop(self):

        self.running = True
        prevtime = time()
        while self.running:
            dt = time() - prevtime
            prevtime = time()
            self._checkInput()
            self._update(dt)
            self._updateUI()
    

    def _checkInput(self):

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.VIDEORESIZE:
                self._resizeDisplay(event.size)
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                for key in self.pressedkeys.keys():
                    if key == event.key:
                        self.pressedkeys[key] = event.type == pg.KEYDOWN
    

    def _update(self, dt):

        if self.pressedkeys[pg.K_SPACE]:
            self.pressedkeys[pg.K_SPACE] = False
            self.paused = not self.paused
        
        if not self.paused:
            self.timesum += dt
            while self.envstate == 0 and self.timesum >= self.speed:
                self.timesum -= self.speed
                self._step()
            if self.envstate == 1 and self.timesum >= 1:
                self._reset()
    

    def _step(self):

        prevstate = self._getState()
        action = self.agent.getAction(prevstate)
        reward = self._playStep(action)
        newstate = self._getState()
        self.agent.memory.remember(prevstate, action, reward, newstate, self.envstate)
        self.agent.train([prevstate], [action], [reward], [newstate], [self.envstate])
        if self.envstate == 1:
            self.agent.trainLong()
            self.agent.sync()
            self.agent.epsilon -= 1
    

    def _getState(self):

        return (
            1 if self.direction[0] == 1 else 0,
            1 if self.direction[1] == 1 else 0,
            1 if self.direction[0] == -1 else 0,
            1 if self.direction[1] == -1 else 0,
            
            1 if (self.direction[0] == 1 and not self._isCollision((self.head[0], self.head[1] - 1))) or
                 (self.direction[1] == 1 and not self._isCollision((self.head[0] + 1, self.head[1]))) or
                 (self.direction[0] == -1 and not self._isCollision((self.head[0], self.head[1] + 1))) or
                 (self.direction[1] == -1 and not self._isCollision((self.head[0] - 1, self.head[1]))) else 0,
            1 if (self.direction[0] == 1 and not self._isCollision((self.head[0] + 1, self.head[1]))) or
                 (self.direction[1] == 1 and not self._isCollision((self.head[0], self.head[1] + 1))) or
                 (self.direction[0] == -1 and not self._isCollision((self.head[0] - 1, self.head[1]))) or
                 (self.direction[1] == -1 and not self._isCollision((self.head[0], self.head[1] - 1))) else 0,
            1 if (self.direction[0] == 1 and not self._isCollision((self.head[0], self.head[1] + 1))) or
                 (self.direction[1] == 1 and not self._isCollision((self.head[0] - 1, self.head[1]))) or
                 (self.direction[0] == -1 and not self._isCollision((self.head[0], self.head[1] - 1))) or
                 (self.direction[1] == -1 and not self._isCollision((self.head[0] + 1, self.head[1]))) else 0,
            
            1 if self.food[0] > self.head[0] else 0,
            1 if self.food[1] > self.head[1] else 0,
            1 if self.food[0] < self.head[0] else 0,
            1 if self.food[1] < self.head[1] else 0
        )


    def _isCollision(self, head):

        if head[0] < 0 or head[0] >= self.w or head[1] < 0 or head[1] >= self.h or head in self.body[:-1]:
            return True
        return False
    

    def _playStep(self, action):

        self._changeDirection(action)
        newhead = self.head[0] + self.direction[0], self.head[1] + self.direction[1]
        if self._isCollision(newhead) or self.wastedsteps == 100:
            self.envstate += 1
            return -2
        elif newhead == self.food:
            self.wastedsteps = 0
            self.score += 1
            if self.score > self.highscore:
                self.highscore = self.score
            self.body.append(self.head)
            self.head = newhead
            self._placeFood()
            return 10
        else:
            self.wastedsteps += 1
            self.body.append(self.head)
            self.body.pop(0)
            aproaching = (self.food[0] - newhead[0]) ** 2 + (self.food[1] - newhead[1]) ** 2 < (self.food[0] - self.head[0]) ** 2 + (self.food[1] - self.head[1]) ** 2
            self.head = newhead
            return -.1
    

    def _changeDirection(self, action):

        if action[0]:
            self.direction = self.direction[1], -self.direction[0]
        elif action[2]:
            self.direction = -self.direction[1], self.direction[0]


    def _updateUI(self):

        self.screen.fill((0, 0, 0, 0))
        for partx, party in self.body:
            pg.draw.rect(self.screen, (0, 0, 255), (self.border + partx * self.tilesize, self.border + party * self.tilesize, self.tilesize, self.tilesize))
        pg.draw.rect(self.screen, (0, 255, 0), (self.border + self.head[0] * self.tilesize, self.border + self.head[1] * self.tilesize, self.tilesize, self.tilesize))
        pg.draw.rect(self.screen, (255, 0, 0), (self.border + self.food[0] * self.tilesize, self.border + self.food[1] * self.tilesize, self.tilesize, self.tilesize))
        for x in range(self.w + 1):
            pg.draw.line(self.screen, (255, 255, 255), (self.border + x * self.tilesize, self.border), (self.border + x * self.tilesize, self.border + self.h * self.tilesize))
        for y in range(self.h + 1):
            pg.draw.line(self.screen, (255, 255, 255), (self.border, self.border + y * self.tilesize), (self.border + self.w * self.tilesize, self.border + y * self.tilesize))

        self.window.fill((55, 55, 55))
        scsurface = pg.transform.smoothscale(self.screen, (self.scx, self.scy))
        offset = (self.winx - self.scx) / 2, (self.winy - self.scy) / 2
        self.window.blit(scsurface, offset)
        pg.display.flip()


if __name__ == "__main__":

    pg.init()
    app = Env()
    app.mainLoop()
    pg.quit()