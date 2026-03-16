import csv
import time
from typing import Dict, Any, List


class DynamicInputReader:
    
    def __init__(self, config: Dict, output_queue, input_delay: float, dataset_path: str):
        self.config = config
        self.output_queue = output_queue
        self.input_delay = input_delay
        self.dataset_path = dataset_path
        self.schema_mapping = config.get("schema_mapping", {})
        self.columns_config = self.schema_mapping.get("columns", [])
        
    def _build_column_map(self, csv_header: List[str]) -> Dict[str, Dict]:
        column_map = {}
        for col_config in self.columns_config:
            source_name = col_config.get("source_name")
            if source_name in csv_header:
                column_map[source_name] = {
                    "internal_mapping": col_config.get("internal_mapping"),
                    "data_type": col_config.get("data_type"),
                    "index": csv_header.index(source_name)
                }
        return column_map
    
    def _cast_value(self, value: str, data_type: str) -> Any:
        try:
            if data_type == "string":
                return str(value).strip()
            elif data_type == "integer":
                return int(value)
            elif data_type == "float":
                return float(value)
            else:
                return value
        except (ValueError, TypeError):
            return None
    
    def _transform_row(self, row: Dict, column_map: Dict) -> Dict:
        data_packet = {}
        for source_name, mapping_config in column_map.items():
            if source_name in row:
                raw_value = row[source_name]
                data_type = mapping_config["data_type"]
                internal_name = mapping_config["internal_mapping"]
                
                casted_value = self._cast_value(raw_value, data_type)
                if casted_value is not None:
                    data_packet[internal_name] = casted_value
        
        return data_packet
    
    def run(self):
        try:
            print(f"[InputModule] Reading dataset from {self.dataset_path}")
            print(f"[InputModule] Schema columns: {[col.get('source_name') for col in self.columns_config]}")
            
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if not reader.fieldnames:
                    raise ValueError("CSV file is empty or has no headers")
                
                print(f"[InputModule] CSV Headers: {list(reader.fieldnames)}")
                
                column_map = self._build_column_map(reader.fieldnames)
                print(f"[InputModule] Matched columns: {list(column_map.keys())}")
                
                if not column_map:
                    raise ValueError(
                        f"No columns matched schema. CSV headers: {reader.fieldnames}"
                    )
                
                row_count = 0
                success_count = 0
                
                for row in reader:
                    try:
                        data_packet = self._transform_row(row, column_map)
                        
                        if data_packet:
                            self.output_queue.put(data_packet, timeout=5)
                            success_count += 1
                            row_count += 1
                            
                            if row_count % 50 == 0:
                                print(f"[InputModule] Processed {row_count} rows | Sent: {success_count}")
                        else:
                            row_count += 1
                            if row_count % 50 == 0:
                                print(f"[InputModule] Processed {row_count} rows | Skipped empty")
                        
                        time.sleep(self.input_delay)
                    
                    except Exception as e:
                        print(f"[InputModule] Row {row_count} error: {e}")
                        continue
                
                print(f"[InputModule] ✓ Completed. Total rows read: {row_count}, Successfully sent: {success_count}")
        
        except FileNotFoundError as e:
            print(f"[InputModule] File not found: {self.dataset_path}")
            print(f"[InputModule] Error: {e}")
        except Exception as e:
            print(f"[InputModule] Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.output_queue.put(None)
            print("[InputModule] Sent end-of-stream signal")
