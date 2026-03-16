import json
import os
import sys
import multiprocessing
import time
from multiprocessing import Queue, Process
from plugins.input_module import DynamicInputReader
from core.signature_verifier import SignatureVerifier
from core.aggregator import StreamAggregator
from plugins.output_module import DashboardVisualizer
from plugins.telemetry import PipelineTelemetry


def load_config(config_path):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Critical Error: config.json is not valid JSON. {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        sys.exit(1)


def orchestrate_pipeline():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")
        config = load_config(config_path)
        
        dataset_path = config.get("dataset_path")
        pipeline_dynamics = config.get("pipeline_dynamics", {})
        input_delay = pipeline_dynamics.get("input_delay_seconds", 0.01)
        core_parallelism = pipeline_dynamics.get("core_parallelism", 4)
        queue_max_size = pipeline_dynamics.get("stream_queue_max_size", 50)
        
        full_dataset_path = os.path.join(base_dir, dataset_path)
        if not os.path.exists(full_dataset_path):
            raise FileNotFoundError(f"Dataset not found at {full_dataset_path}")
        
        raw_data_stream = Queue(maxsize=queue_max_size)
        processed_data_stream = Queue(maxsize=queue_max_size)
        
        telemetry = PipelineTelemetry(
            raw_data_stream=raw_data_stream,
            processed_data_stream=processed_data_stream,
            config=config
        )
        
        input_reader = DynamicInputReader(
            config=config,
            output_queue=raw_data_stream,
            input_delay=input_delay,
            dataset_path=full_dataset_path
        )
        
        verifier = SignatureVerifier(
            config=config,
            input_queue=raw_data_stream,
            output_queue=processed_data_stream
        )
        
        aggregator = StreamAggregator(
            config=config,
            input_queue=processed_data_stream
        )
        
        dashboard = DashboardVisualizer(
            config=config,
            telemetry=telemetry,
            aggregator=aggregator
        )
        
        processes = []
        
        input_process = Process(
            target=input_reader.run,
            name="InputModule",
            daemon=False
        )
        processes.append(input_process)
        
        for i in range(core_parallelism):
            core_process = Process(
                target=verifier.run,
                name=f"CoreWorker-{i}",
                daemon=False
            )
            processes.append(core_process)
        
        aggregator_process = Process(
            target=aggregator.run,
            name="AggregatorModule",
            daemon=False
        )
        processes.append(aggregator_process)
        
        dashboard_process = Process(
            target=dashboard.run,
            name="DashboardModule",
            daemon=False
        )
        processes.append(dashboard_process)
        
        print("🚀 Starting Phase 3 Concurrent Pipeline...")
        print(f"   Input Delay: {input_delay}s")
        print(f"   Core Workers: {core_parallelism}")
        print(f"   Queue Capacity: {queue_max_size}")
        print(f"   Dataset: {dataset_path}\n")
        
        for process in processes:
            process.start()
            print(f"   ✓ {process.name} started")
        
        print("\n📊 Pipeline Running. Press Ctrl+C to stop.\n")
        
        try:
            while True:
                telemetry.update()
                
                all_alive = all(p.is_alive() for p in processes)
                if not all_alive:
                    print("\n⏹️  All processes completed!")
                    break
                
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down pipeline...")
        
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)
                    if process.is_alive():
                        process.kill()
                        process.join(timeout=1)
            
            print("✓ All processes terminated")
    
    except Exception as e:
        print(f"Orchestration Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    orchestrate_pipeline()
