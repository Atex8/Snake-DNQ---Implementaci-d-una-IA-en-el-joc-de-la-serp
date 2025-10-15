from copy import deepcopy
from random import random
import numpy as np


class DeepQNNet:

    def __init__(self, dim, lr, weights = None, biases = None):

        self.dim = dim
        self.weights = deepcopy(weights) if weights else [np.random.uniform(-.5, .5, (dim[l + 1], dim[l])) for l in range(len(dim) - 1)]
        self.biases = deepcopy(biases) if biases else [np.zeros((self.dim[l + 1], 1)) for l in range(len(dim) - 1)]
        self.e = 2.7182818284
        self.lr = lr


    def activationFunction(self, z):

        return 1 / (1 + self.e ** (-z))

    
    def derivativeActivationFunction(self, z):

        return self.activationFunction(z) * (1 - self.activationFunction(z))


    def forward(self, inputl):

        a = np.array(inputl).reshape(-1, 1)
        zs = [a]
        activations = [a]
        for l in range(len(self.dim) - 1):
            z = np.dot(self.weights[l], a) + self.biases[l]
            zs.append(z)
            if l == len(self.dim) - 2:
                a = z
            else:
                a = self.activationFunction(z)
            activations.append(a)
        return zs, activations


    def backward(self, dloss, zs, activations):

        dz = dloss
        for l in reversed(range(len(self.dim) - 1)):
            dw = np.dot(dz, activations[l].T)
            cdw = np.clip(dw, -1, 1)
            cdb = np.clip(dz, -1, 1)
            dz = np.dot(self.weights[l].T, dz) * self.derivativeActivationFunction(zs[l])
            self.weights[l] -= self.lr * cdw
            self.biases[l] -= self.lr * cdb