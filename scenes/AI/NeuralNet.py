class DeepQNNet:

    def __init__(self):

        self.e = 2.7182818284


    def activationFunction(self, z):

        return 1 / (1 + self.e ^ (-z))

    
    def derivativeActivationFunction(self, z):

        return self.activationFunction(z) * (1 - self.activationFunction(z))


    def forward(self):

        pass


    def backward(self):

        pass