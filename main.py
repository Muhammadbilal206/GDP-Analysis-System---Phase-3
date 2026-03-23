import json
import multiprocessing
import sys
import time
from queue import Empty

from plugins.input_module import DataIngestor
from core.signature_verifier import AuthWorker
from core.aggregator import StreamReassembler
from plugins.telemetry import QueueMonitor
from plugins.output_module import LiveVisualizer

def start_ingestion(cfg, q_raw, workers):
    ingestor = DataIngestor(cfg)
    ingestor.execute(q_raw, workers)

def start_verification(cfg, q_raw, q_verified):
    worker = AuthWorker(cfg)
    worker.execute(q_raw, q_verified)

def start_aggregation(cfg, workers, q_verified, q_processed):
    reassembler = StreamReassembler(cfg, workers)
    reassembler.execute(q_verified, q_processed)

def terminal_probe(cfg, max_frames=200, wait=0.2):
    limit = cfg["pipeline_dynamics"]["stream_queue_max_size"]
    workers = cfg["pipeline_dynamics"]["core_parallelism"]

    q_raw = multiprocessing.Queue(maxsize=limit)
    q_verified = multiprocessing.Queue(maxsize=limit)
    q_processed = multiprocessing.Queue(maxsize=limit)

    processes = [multiprocessing.Process(target=start_ingestion, args=(cfg, q_raw, workers))]
    for _ in range(workers):
        processes.append(multiprocessing.Process(target=start_verification, args=(cfg, q_raw, q_verified)))
    processes.append(multiprocessing.Process(target=start_aggregation, args=(cfg, workers, q_verified, q_processed)))

    for p in processes:
        p.start()

    items_read = 0
    for frame in range(max_frames):
        if frame % 5 == 0:
            print(f"[T={frame}] Status => Ingestion: {q_raw.qsize()}/{limit} | Auth: {q_verified.qsize()}/{limit} | Aggregation: {q_processed.qsize()}/{limit} | Handled: {items_read}")

        for _ in range(2):
            try:
                data = q_processed.get_nowait()
                if data is None:
                    print(f"\n[SYSTEM] Pipeline execution completed at tick {frame}. Total handled: {items_read}")
                    for p in processes:
                        p.join(timeout=2)
                    return
                items_read += 1
            except Empty:
                break
        time.sleep(wait)

if __name__ == "__main__":
    with open("config.json", "r") as file_obj:
        app_config = json.load(file_obj)

    if "--stream-test" in sys.argv:
        terminal_probe(app_config)
        sys.exit(0)

    capacity = app_config["pipeline_dynamics"]["stream_queue_max_size"]
    worker_count = app_config["pipeline_dynamics"]["core_parallelism"]

    q_raw = multiprocessing.Queue(maxsize=capacity)
    q_verified = multiprocessing.Queue(maxsize=capacity)
    q_processed = multiprocessing.Queue(maxsize=capacity)

    p_ingest = multiprocessing.Process(target=start_ingestion, args=(app_config, q_raw, worker_count))
    
    p_auths = []
    for _ in range(worker_count):
        p = multiprocessing.Process(target=start_verification, args=(app_config, q_raw, q_verified))
        p_auths.append(p)

    p_agg = multiprocessing.Process(target=start_aggregation, args=(app_config, worker_count, q_verified, q_processed))

    p_ingest.start()
    for p in p_auths:
        p.start()
    p_agg.start()

    monitor = QueueMonitor({"raw": q_raw, "verified": q_verified, "processed": q_processed}, capacity)
    dashboard = LiveVisualizer(app_config, q_processed, monitor)
    
    dashboard.launch()

    for p in [p_ingest, p_agg] + p_auths:
        p.join(timeout=2)
        if p.is_alive():
            p.terminate()
