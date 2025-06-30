from pygame import Surface


class SceneTemplate:

    def __init__(self, app):

        self.app = app


    def quitScene(self):

        self.app.stack.pop()
    

    def resize(self, size):

        pass

    
    def update(self, dt):

        pass


    def render(self, display):

        pass