from copy import deepcopy
from random import random


class DeepQNNet:

    def __init__(self, dim, weights = None, biases = None):

        self.dim = dim
        self.weights = deepcopy(weights) if weights else [[[2 * random() - 1 for k in range(dim[l])] for j in range(dim[l + 1])] for l in range(len(dim) - 1)]
        self.biases = deepcopy(biases) if biases else [[2 * random() - 1 for j in range(dim[l + 1])] for l in range(len(dim) - 1)]
        self.e = 2.7182818284
        self.lr = .001


    def activationFunction(self, z):

        return 1 / (1 + self.e ** (-z))

    
    def derivativeActivationFunction(self, z):

        return self.activationFunction(z) * (1 - self.activationFunction(z))


    def forward(self, inputl):

        zs = [inputl]
        activations = [inputl]
        for l in range(len(self.dim) - 1):
            lz = []
            la = []
            for j in range(self.dim[l + 1]):
                z = self.biases[l][j]
                for k in range(self.dim[l]):
                    z += self.weights[l][j][k] * activations[l][k]
                lz.append(z)
                if l == len(self.dim) - 2:
                    la.append(z)
                else:
                    la.append(self.activationFunction(z))
            zs.append(lz)
            activations.append(la)
        return zs, activations


    def backward(self, dloss, zs, activations):

        dz = dloss
        for l in range(len(self.dim) - 2, -1, -1):
            newdz = [0] * self.dim[l]
            for j in range(self.dim[l + 1]):
                for k in range(self.dim[l]):
                    newdz[k] += self.weights[l][j][k] * dz[j]
                    self.weights[l][j][k] -= self.lr * dz[j] * activations[l][k]
                self.biases[l][j] -= self.lr * dz[j]
            dz = [newdz[k] * self.derivativeActivationFunction(zs[l][k]) for k in range(self.dim[l])]