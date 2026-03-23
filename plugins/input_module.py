import csv
import time

TYPE_MAP = {
    "string": str,
    "integer": int,
    "float": float
}

class DataIngestor:
    def __init__(self, config_data):
        self.filepath = config_data["dataset_path"]
        self.schema = config_data["schema_mapping"]["columns"]
        self.sleep_time = config_data["pipeline_dynamics"]["input_delay_seconds"]

    def execute(self, q_out, worker_count):
        with open(self.filepath, mode="r", encoding="utf-8") as file_obj:
            csv_reader = csv.DictReader(file_obj)
            
            for index, row_data in enumerate(csv_reader):
                parsed_record = self._transform(row_data, index)
                q_out.put(parsed_record)
                time.sleep(self.sleep_time)

        for _ in range(worker_count):
            q_out.put(None)

    def _transform(self, row_data, index):
        record = {"_seq": index}
        for field in self.schema:
            raw_val = row_data[field["source_name"]]
            cast_func = TYPE_MAP[field["data_type"]]
            record[field["internal_mapping"]] = cast_func(raw_val)
        return record
