# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import sys
import os
import time
import psutil
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def run_tests_with_metrics(test_path: str, output_file: str):
    print(f"Running tests in {test_path}...")
    
    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss / 1024 / 1024
    start_cpu = process.cpu_percent(interval=None)
    start_time = time.time()
    
    # Run pytest
    # We use -v for verbose, -p no:warnings to reduce noise
    retcode = pytest.main(["-v", "-p", "no:warnings", test_path])
    
    end_time = time.time()
    end_mem = process.memory_info().rss / 1024 / 1024
    end_cpu = process.cpu_percent(interval=None)
    
    duration = end_time - start_time
    mem_delta = end_mem - start_mem
    
    metrics = {
        "test_path": test_path,
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "memory_start_mb": start_mem,
        "memory_end_mb": end_mem,
        "memory_delta_mb": mem_delta,
        "cpu_percent": end_cpu, # Snapshot at end
        "return_code": retcode
    }
    
    print(f"\nMetrics for {test_path}:")
    print(json.dumps(metrics, indent=2))
    
    # Append to output file
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
        
    data.append(metrics)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
        
    return retcode

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_audit_tests.py <test_path>... [output_file.json]")
        sys.exit(1)
        
    args = sys.argv[1:]
    output_file = "audit_metrics.json"
    test_paths = []
    
    # Check if last argument is a json file
    if args[-1].endswith('.json'):
        output_file = args[-1]
        test_paths = args[:-1]
    else:
        test_paths = args
        
    final_retcode = 0
    for path in test_paths:
        ret = run_tests_with_metrics(path, output_file)
        if ret != 0:
            final_retcode = ret
            
    sys.exit(final_retcode)
