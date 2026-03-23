from .functional_core import calc_moving_mean

class StreamReassembler:
    def __init__(self, config_data, worker_count):
        self.limit = config_data["processing"]["stateful_tasks"]["running_average_window_size"]
        self.worker_count = worker_count
        self.history = []
        self.stash = {}
        self.expected_seq = 0

    def execute(self, q_in, q_out):
        end_signals = 0
        
        while True:
            item = q_in.get()
            
            if item is None:
                end_signals += 1
                if end_signals >= self.worker_count:
                    self._purge_stash(q_out)
                    q_out.put(None)
                    break
                continue

            self.stash[item["_seq"]] = item
            self._purge_stash(q_out)

    def _purge_stash(self, q_out):
        while self.expected_seq in self.stash:
            current_item = self.stash.pop(self.expected_seq)
            self.expected_seq += 1

            if current_item.get("_dropped"):
                continue

            self.history.append(current_item["metric_value"])
            if len(self.history) > self.limit:
                self.history.pop(0)

            current_item["computed_metric"] = calc_moving_mean(self.history)
            q_out.put(current_item)
