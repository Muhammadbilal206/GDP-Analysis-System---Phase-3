from collections import deque
from typing import Dict
from core.functional_core import FunctionalCore


class ImperativeShell:
    
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.sliding_window = deque(maxlen=window_size)
        self.processing_count = 0
    
    def process_value(self, value: float) -> float:
        self.window_copy, avg = FunctionalCore.calculate_sliding_window(
            value, 
            self.sliding_window, 
            self.window_size
        )
        self.sliding_window = self.window_copy
        self.processing_count += 1
        return avg


class StreamAggregator:
    
    def __init__(self, config: Dict, input_queue):
        self.config = config
        self.input_queue = input_queue
        
        stateful_config = config.get("processing", {}).get("stateful_tasks", {})
        window_size = stateful_config.get("running_average_window_size", 10)
        
        self.aggregator = ImperativeShell(window_size=window_size)
        self.last_computed_value = None
        self.last_computed_average = None
    
    def run(self):
        try:
            print(f"[StreamAggregator] Started with window size: {self.aggregator.window_size}")
            
            while True:
                data_packet = self.input_queue.get()
                
                if data_packet is None:
                    break
                
                metric_value = data_packet.get("metric_value")
                
                if metric_value is not None:
                    running_avg = self.aggregator.process_value(metric_value)
                    
                    self.last_computed_value = metric_value
                    self.last_computed_average = running_avg
                    
                    data_packet["computed_metric"] = running_avg
                    data_packet["window_size"] = self.aggregator.window_size
                    
                    if self.aggregator.processing_count % 100 == 0:
                        print(f"[StreamAggregator] Processed {self.aggregator.processing_count} packets | Latest Avg: {running_avg:.2f}")
        
        except Exception as e:
            print(f"[StreamAggregator] Error: {e}")
        
        finally:
            print(f"[StreamAggregator] ✓ Completed. Total: {self.aggregator.processing_count}")
