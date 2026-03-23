class FunctionalCore:
    @staticmethod
    def calculate_average(window):
        return sum(window) / len(window) if window else 0.0
