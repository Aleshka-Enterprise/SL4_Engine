from game.models.text.text import Text


class Counter(Text):
    def __init__(self, score: int = 0, **kwargs):
        super().__init__(**kwargs)

        self.score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self.text = str(value)
