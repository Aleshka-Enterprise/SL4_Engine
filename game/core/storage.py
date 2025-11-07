class GameStorage:
    def __init__(self):
        self.player = None
        self.camera = None
        self.grounds = []
        self.items = []
        self.entities = []
        self.shots = []
        self.particles = []
        
        self.render_objects_list = []
        self.collision_object_list = []

class GAME_STATE:
    ''' Общее состаяние игры '''
    IS_PAUSED = False
    IS_RUNNING = True

class LEVEL_STATE:
    ''' Состояние уровня '''

storage = GameStorage()
