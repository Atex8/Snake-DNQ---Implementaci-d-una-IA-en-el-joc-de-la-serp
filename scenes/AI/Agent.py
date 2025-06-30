from .NeuralNet import DeepQNNet


class Agent:

    def __init__(self):

        self.policyNet = DeepQNNet()
        self.targetNet = DeepQNNet()


    def chooseAction(self, state):

        return 0, 0, 1