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

import unittest
import os
import sys
import time
from typing import Dict, Any, List

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
print(f"Debug: Added {root_dir} to sys.path")

try:
    from audit.phase4.reporters.markdown_reporter import MarkdownReporter
except ImportError:
    # Fallback for when running directly from the directory
    sys.path.append(os.path.join(os.path.dirname(__file__), 'reporters'))
    from markdown_reporter import MarkdownReporter

from symbo_agentic_reasoners_phase4.phase4_system import Phase4System

class AuditTestResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.results = []

    def startTest(self, test):
        self._start_time = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        duration = time.time() - self._start_time
        self.results.append({
            'test_name': test._testMethodName,
            'file': os.path.basename(sys.modules[test.__module__].__file__),
            'status': 'PASS',
            'duration': duration,
            'message': None
        })
        super().addSuccess(test)

    def addFailure(self, test, err):
        duration = time.time() - self._start_time
        self.results.append({
            'test_name': test._testMethodName,
            'file': os.path.basename(sys.modules[test.__module__].__file__),
            'status': 'FAIL',
            'duration': duration,
            'message': str(err[1])
        })
        super().addFailure(test, err)

    def addError(self, test, err):
        duration = time.time() - self._start_time
        self.results.append({
            'test_name': test._testMethodName,
            'file': os.path.basename(sys.modules[test.__module__].__file__),
            'status': 'ERROR',
            'duration': duration,
            'message': str(err[1])
        })
        super().addError(test, err)

def run_audit():
    print("=" * 80)
    print("PHASE 4 AUDIT INITIATED")
    print("=" * 80)
    print(f"Target: Dynamic Governance & Resilience")
    print()

    # Discover tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='*_tests.py')

    # Run tests
    result = AuditTestResult()
    suite.run(result)

    # Collect stats
    run_stats = {
        'total': result.testsRun,
        'passed': len([r for r in result.results if r['status'] == 'PASS']),
        'failed': len(result.failures),
        'errors': len(result.errors),
        'results': result.results
    }

    print("Collecting system statistics...")
    try:
        system = Phase4System()
        system.start()
        system_stats = system.get_statistics()
        system.shutdown()
    except Exception as e:
        print(f"Warning: Could not collect system stats: {e}")
        system_stats = {}

    # Generate Report
    reporter = MarkdownReporter(os.path.join(os.path.dirname(__file__), 'reports'))
    report_path = reporter.generate_report(run_stats, system_stats)

    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print(f"Report generated: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    run_audit()
