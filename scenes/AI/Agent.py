from random import randint, sample
from copy import deepcopy
from .NeuralNet import DeepQNNet


class ReplayBuffer:

    def __init__(self, maxlen):

        self.memory = []
        self.maxlen = maxlen


    def remember(self, prevstate, action, reward, newstate, done):

        self.memory.append((prevstate, action, reward, newstate, done))
        if len(self.memory) > self.maxlen:
            self.memory.pop(0)


class Agent:

    def __init__(self, policyWeights = None, policyBiases = None, targetWeights = None, targetBiases = None):

        self.epsilon = 80
        self.gamma = .1
        self.batchsize = 1000
        self.dim = 11, 128, 64, 3

        self.memory = ReplayBuffer(100_000)
        if policyWeights:
            self.policyNet = DeepQNNet(self.dim, policyWeights, policyBiases)
            self.targetNet = DeepQNNet(self.dim, targetWeights, targetBiases)
        else:
            self.policyNet = DeepQNNet(self.dim)
            self.sync()
    

    def sync(self):

        self.targetNet = DeepQNNet(self.dim, self.policyNet.weights, self.policyNet.biases)


    def chooseAction(self, state):

        action = [0, 0, 0]
        if randint(0, 100) <= self.epsilon:
            arg = randint(0, 2)
        else:
            result = self.policyNet.forward(state)[1][-1]
            arg = result.index(max(result))
        action[arg] = 1
        return tuple(action)
    

    def train(self, prevstate, action, reward, newstate, done):

        for i in range(len(done)):
            zs, activations = self.policyNet.forward(prevstate[i])
            Qval = activations[-1]
            target = deepcopy(Qval)
            target[action[i].index(max(action[i]))] = reward[i]
            if not done[i]:
                target[action[i].index(max(action[i]))] += self.gamma * max(self.targetNet.forward(newstate[i])[1][-1])
            dloss = [2 * (Qval[_] - target[_]) for _ in range(self.dim[-1])]
            self.policyNet.backward(dloss, zs, activations)


    def train_long(self):

        if len(self.memory.memory) >= self.batchsize:
            minibatch = sample(self.memory.memory, self.batchsize)
        else:
            minibatch = self.memory.memory
        prevstate, action, reward, newstate, done = zip(*minibatch)
        self.train(prevstate, action, reward, newstate, done)