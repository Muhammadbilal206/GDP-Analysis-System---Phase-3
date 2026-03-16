import time
from collections import deque
from typing import Dict


class DashboardVisualizer:
    
    def __init__(self, config: Dict, telemetry, aggregator):
        self.config = config
        self.telemetry = telemetry
        self.aggregator = aggregator
        
        viz_config = config.get("visualizations", {})
        self.telemetry_config = viz_config.get("telemetry", {})
        self.data_charts = viz_config.get("data_charts", [])
        
        self.time_series_values = deque(maxlen=200)
        self.time_series_averages = deque(maxlen=200)
        
        self.queue_history = deque(maxlen=50)
    
    def _get_queue_health(self, queue_size: int, max_size: int) -> str:
        percentage = (queue_size / max_size * 100) if max_size > 0 else 0
        
        if percentage < 50:
            return "🟢 Flowing"
        elif percentage < 80:
            return "🟡 Filling"
        else:
            return "🔴 Backpressure"
    
    def _render_telemetry_view(self):
        if self.telemetry_config.get("show_raw_stream"):
            raw_size = self.telemetry.raw_stream_size
            raw_max = self.telemetry.raw_stream_max_size
            health = self._get_queue_health(raw_size, raw_max)
            print(f"  📤 Raw Stream: [{raw_size}/{raw_max}] {health}")
        
        if self.telemetry_config.get("show_intermediate_stream"):
            proc_size = self.telemetry.processed_stream_size
            proc_max = self.telemetry.processed_stream_max_size
            health = self._get_queue_health(proc_size, proc_max)
            print(f"  ⚙️  Processed Stream: [{proc_size}/{proc_max}] {health}")
    
    def _render_data_charts(self):
        if self.aggregator.last_computed_value is not None:
            print(f"  📊 Latest Sensor Value: {self.aggregator.last_computed_value:.2f}")
        else:
            print(f"  📊 Latest Sensor Value: Awaiting data...")
        
        if self.aggregator.last_computed_average is not None:
            print(f"  📈 Latest Running Average: {self.aggregator.last_computed_average:.2f}")
        else:
            print(f"  📈 Latest Running Average: Awaiting data...")
    
    def run(self):
        try:
            print("\n[Dashboard] Visualization Started\n")
            print("=" * 60)
            print("              PHASE 3 PIPELINE DASHBOARD")
            print("=" * 60)
            
            iteration = 0
            while True:
                iteration += 1
                
                print(f"\n[Frame {iteration}] {time.strftime('%H:%M:%S')}")
                
                print("\n  STREAM TELEMETRY:")
                self._render_telemetry_view()
                
                print("\n  DATA VISUALIZATIONS:")
                self._render_data_charts()
                
                print("\n" + "=" * 60)
                time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n[Dashboard] Shutting down...")
        except Exception as e:
            print(f"[Dashboard] Error: {e}")
        finally:
            print("[Dashboard] ✓ Closed")
