import json
import multiprocessing
import csv
import time
from multiprocessing import Process, Queue, Value
from plugins.output_module import Visualizer
from plugins.telemetry import PipelineTelemetry
from core.signature_verifier import SignatureVerifier
from core.aggregator import Aggregator

def run_input(cfg, q, count):
    with open(cfg['dataset_path'], 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            packet = {"entity_name": row["Sensor_ID"], "metric_value": float(row["Raw_Value"]), 
                      "security_hash": row["Auth_Signature"]}
            q.put(packet)
            with count.get_lock(): count.value += 1
            time.sleep(cfg['pipeline_dynamics']['input_delay_seconds'])
    for _ in range(cfg['pipeline_dynamics']['core_parallelism']): q.put(None)

def run_core(cfg, in_q, out_q, in_cnt, out_cnt):
    v = SignatureVerifier(cfg['processing']['stateless_tasks']['secret_key'], cfg['processing']['stateless_tasks']['iterations'])
    a = Aggregator(cfg['processing']['stateful_tasks']['running_average_window_size'])
    while True:
        p = in_q.get()
        with in_cnt.get_lock(): 
            if in_cnt.value > 0: in_cnt.value -= 1
        if p is None: break
        if v.verify(p['metric_value'], p['security_hash']):
            p['computed_metric'] = a.process(p['metric_value'])
            out_q.put(p)
            with out_cnt.get_lock(): out_cnt.value += 1

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    with open('config.json', 'r') as f: config = json.load(f)
    limit = config['pipeline_dynamics']['stream_queue_max_size']
    raw_q, proc_q = Queue(maxsize=limit), Queue(maxsize=limit)
    raw_cnt, proc_cnt = Value('i', 0), Value('i', 0)
    
    tel = PipelineTelemetry(raw_cnt, proc_cnt, limit)
    Process(target=run_input, args=(config, raw_q, raw_cnt)).start()
    for _ in range(config['pipeline_dynamics']['core_parallelism']):
        Process(target=run_core, args=(config, raw_q, proc_q, raw_cnt, proc_cnt)).start()

    Visualizer(tel, proc_q, raw_cnt, proc_cnt).run()
