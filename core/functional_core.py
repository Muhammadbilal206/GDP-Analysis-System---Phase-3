import statistics
from typing import List
from collections import deque


class FunctionalCore:
    
    @staticmethod
    def calculate_running_average(values: List[float]) -> float:
        if not values:
            return 0.0
        return statistics.mean(values)
    
    @staticmethod
    def calculate_sliding_window(current_value: float, window: deque, window_size: int) -> tuple:
        window_copy = deque(window, maxlen=window_size)
        window_copy.append(current_value)
        average = FunctionalCore.calculate_running_average(list(window_copy))
        return window_copy, average
