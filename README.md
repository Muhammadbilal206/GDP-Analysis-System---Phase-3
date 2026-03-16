# GDP-Analysis-System---Phase-3
Elevate GDP analysis system into a generalized, concurrent data-processing pipeline.
# Phase 3: Generic Concurrent Real-Time Pipeline

## Project Setup

### 1. Directory Structure
Project_root/
├── main.py
├── config.json
├── readme.txt
├── data/
│   └── sample_sensor_data.csv
├── core/
│   ├── __init__.py
│   ├── functional_core.py
│   ├── signature_verifier.py
│   └── aggregator.py
└── plugins/
    ├── __init__.py
    ├── input_module.py
    ├── output_module.py
    └── telemetry.py

### 2. Installation

A. Install Dependencies
pip install -r requirements.txt

B. Prepare Data
Place your CSV file in data/ directory
Update config.json with the dataset path and schema mapping

C. Run the Pipeline
cd Project_root
python main.py

### 3. Configuration

Edit config.json:
- dataset_path: Path to your CSV file
- input_delay_seconds: Delay between row reads
- core_parallelism: Number of verification workers
- stream_queue_max_size: Maximum queue size before backpressure
- schema_mapping: Map CSV columns to internal generic names

### 4. Data Streams

Raw Data Stream: Input → Core
- CSV rows mapped to generic variables
- Bounded queue

Processed Data Stream: Core → Output
- Verified & aggregated data
- Bounded queue

### 5. Backpressure

Bounded queues automatically throttle upstream:
- 🟢 Flowing: < 50% capacity
- 🟡 Filling: 50-80% capacity
- 🔴 Backpressure: > 80% capacity

### 6. Cryptographic Verification

Algorithm: PBKDF2-HMAC SHA-256
Iterations: 100,000
Password: secret_key from config.json
Salt: raw_value rounded to 2 decimal places
Unverified packets: Automatically dropped

### 7. Running Average

Window Size: 10 (configurable)
Pattern: Functional Core + Imperative Shell
- Pure function: FunctionalCore.calculate_sliding_window()
- State management: ImperativeShell.process_value()

### 8. Design Patterns

✅ Dependency Inversion Principle
✅ Producer-Consumer
✅ Scatter-Gather
✅ Functional Core + Imperative Shell
✅ Observer Pattern

### 9. Monitoring

Dashboard displays (updates every 2 seconds):
- Raw stream queue size and health
- Processed stream queue size and health
- Latest sensor values (verified packets only)
- Latest running averages
- Real-time backpressure indicators

### 10. Team Branches

Bilal - Core & Verification:
- core/functional_core.py
- core/signature_verifier.py
- core/aggregator.py
- main.py

Usman - Input/Output & Telemetry:
- plugins/input_module.py
- plugins/output_module.py
- plugins/telemetry.py

Both - Configuration & Data:
- config.json
- readme.txt
- data/sample_sensor_data.csv

### 11. GitHub Repository
https://github.com/Muhammadbilal206/GDP-Analysis-System---Phase-3

---

Phase 3 Complete! 🎉
