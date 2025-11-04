class GameStorage:
    def __init__(self):
        self.player = None
        self.camera = None
        self.game_options = {
            'running': True,
        }
        self.grounds = []
        self.items = []
        self.entities = []
        self.shots = []
        self.particles = []
        
        self.render_objects_list = []
        self.collision_object_list = []

storage = GameStorage()
