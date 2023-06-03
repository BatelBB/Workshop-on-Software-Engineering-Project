

class NeverTwice:
    def __init__(self):
        self._count = 0

    def __call__(self):
        self._count += 1
        if self._count > 1:
            raise Exception("NeverTwiced happened twice!")
