from core.functional_core import FunctionalCore

class Aggregator:
    def __init__(self, window_size):
        self.window_size = window_size
        self.history = []

    def process(self, value):
        self.history.append(value)
        if len(self.history) > self.window_size:
            self.history.pop(0)
        return FunctionalCore.calculate_average(self.history)
