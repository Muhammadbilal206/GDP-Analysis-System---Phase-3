class QueueMonitor:
    def __init__(self, queue_dict, capacity):
        self.queue_dict = queue_dict
        self.capacity = capacity
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def trigger_update(self):
        status = {name: q.qsize() for name, q in self.queue_dict.items()}
        for listener in self.listeners:
            listener.refresh_telemetry(status)
