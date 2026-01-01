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

import time
import psutil
import os
import functools
import logging
import json
from typing import Any, Callable, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuditMetrics:
    def __init__(self):
        self.metrics = {}

    def record(self, name: str, data: Dict[str, Any]):
        self.metrics[name] = data

    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)

def measure_resources(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent(interval=None)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            status = "SUCCESS"
        except Exception as e:
            result = None
            status = f"ERROR: {str(e)}"
            raise e
        finally:
            end_time = time.time()
            end_mem = process.memory_info().rss / 1024 / 1024 # MB
            end_cpu = process.cpu_percent(interval=None)
            
            duration = end_time - start_time
            mem_delta = end_mem - start_mem
            
            logger.info(f"Function {func.__name__} finished in {duration:.4f}s. Memory delta: {mem_delta:.2f}MB. Status: {status}")
            
            # You might want to store this somewhere global or return it
            # For now, just logging
            
        return result
    return wrapper

def get_system_metrics() -> Dict[str, Any]:
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "available_memory_mb": psutil.virtual_memory().available / 1024 / 1024
    }
