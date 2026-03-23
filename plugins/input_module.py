import csv
import time

class InputModule:
    def __init__(self, config):
        self.config = config

    def run(self, raw_queue):
        with open(self.config['dataset_path'], 'r') as f:
            reader = csv.DictReader(f)
            cols = self.config['schema_mapping']['columns']
            for row in reader:
                packet = {}
                for c in cols:
                    val = row[c['source_name']]
                    if c['data_type'] == 'float': val = float(val)
                    elif c['data_type'] == 'integer': val = int(val)
                    packet[c['internal_mapping']] = val
                raw_queue.put(packet)
                time.sleep(self.config['pipeline_dynamics']['input_delay_seconds'])
        raw_queue.put(None)
