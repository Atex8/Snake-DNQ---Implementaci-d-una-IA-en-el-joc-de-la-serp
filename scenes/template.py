from pygame import Surface


class SceneTemplate:

    def __init__(self, app):

        self.app = app


    def quitScene(self):

        self.app.stack.pop()

    
    def update(self, dt):

        pass


    def render(self):

        return Surface(self.app.dim)