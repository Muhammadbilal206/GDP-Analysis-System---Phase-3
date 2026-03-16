from typing import Dict
from multiprocessing import Queue


class PipelineTelemetry:
    
    def __init__(self, raw_data_stream: Queue, processed_data_stream: Queue, config: Dict):
        self.raw_stream = raw_data_stream
        self.processed_stream = processed_data_stream
        self.config = config
        
        self.raw_stream_size = 0
        self.raw_stream_max_size = config.get("pipeline_dynamics", {}).get("stream_queue_max_size", 50)
        
        self.processed_stream_size = 0
        self.processed_stream_max_size = config.get("pipeline_dynamics", {}).get("stream_queue_max_size", 50)
        
        self.observers = []
    
    def attach_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)
    
    def detach_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            try:
                observer.update(
                    raw_stream_size=self.raw_stream_size,
                    processed_stream_size=self.processed_stream_size
                )
            except Exception as e:
                pass
    
    def update(self):
        try:
            self.raw_stream_size = self.raw_stream.qsize()
            self.processed_stream_size = self.processed_stream.qsize()
            self.notify_observers()
        except Exception:
            pass
