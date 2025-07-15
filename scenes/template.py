class SceneTemplate:

    def __init__(self, app):

        self.app = app


    def quitScene(self):

        self.app.stack.pop()
    

    def addScene(self, scene):

        self.app.stack.append(scene)
    

    def resize(self, size):

        if size[0] / size[1] > self.rel:
            self.scale = size[1] / self.app.defaultDim[1]
        else:
            self.scale = size[0] / self.app.defaultDim[0]

    
    def update(self, dt):

        pass


    def render(self, display):

        pass