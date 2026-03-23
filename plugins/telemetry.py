class PipelineTelemetry:
    def __init__(self, raw_count, proc_count, max_size):
        self.raw_count = raw_count
        self.proc_count = proc_count
        self.max_size = max_size

    def get_status(self):
        return {
            "raw": self.raw_count.value, 
            "proc": self.proc_count.value, 
            "limit": self.max_size
        }
