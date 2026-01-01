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
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List
import shutil

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
print(f"Debug: Added {root_dir} to sys.path")

from audit.phase6.reporters.markdown_reporter import MarkdownReporter
try:
    from symbo_agentic_reasoners_phase6.phase6_system import Phase6System
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import Phase6System: {e}")
    print("Ensure symbo_agentic_reasoners_phase6 package is in the python path.")
    sys.exit(1)

class AuditTestResult(unittest.TestResult):
    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super(AuditTestResult, self).__init__(stream, descriptions, verbosity)
        self.audit_results = []
        self._start_time = None

    def startTest(self, test):
        self._start_time = time.time()
        super(AuditTestResult, self).startTest(test)

    def addSuccess(self, test):
        duration = time.time() - self._start_time if self._start_time else 0.0
        super(AuditTestResult, self).addSuccess(test)
        self.audit_results.append({
            'test_case': test._testMethodName,
            'status': 'PASS',
            'duration': duration,
            'message': ''
        })

    def addFailure(self, test, err):
        duration = time.time() - self._start_time if self._start_time else 0.0
        super(AuditTestResult, self).addFailure(test, err)
        self.audit_results.append({
            'test_case': test._testMethodName,
            'status': 'FAIL',
            'duration': duration,
            'message': str(err[1]).split('\n')[-2] if len(str(err[1]).split('\n')) > 1 else str(err[1])
        })

    def addError(self, test, err):
        duration = time.time() - self._start_time if self._start_time else 0.0
        super(AuditTestResult, self).addError(test, err)
        self.audit_results.append({
            'test_case': test._testMethodName,
            'status': 'ERROR',
            'duration': duration,
            'message': str(err[1]).split('\n')[-2] if len(str(err[1]).split('\n')) > 1 else str(err[1])
        })

class AuditResultObj:
    def __init__(self, test_case, status, duration, message=""):
        self.test_case = test_case
        self.status = status
        self.duration = duration
        self.message = message

def run_audit():
    print("="*80)
    print("PHASE 6 AUDIT: The Mathematical Discovery Engine")
    print("="*80)

    # 1. Discover Tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='*_tests.py')
    
    print(f"Discovered {suite.countTestCases()} tests.")

    # 2. Run Tests
    runner = unittest.TextTestRunner(resultclass=AuditTestResult, verbosity=2)
    result = runner.run(suite)
    
    # Convert dict results to objects for reporter
    final_results = []
    for r in result.audit_results:
        final_results.append(AuditResultObj(r['test_case'], r['status'], r['duration'], r['message']))

    # 3. Collect System Statistics
    print("\nCollecting System Statistics...")
    try:
        # Instantiate system to get stats
        system = Phase6System()
        try:
            system.start()
            # Run a tiny cycle to populate some stats if empty
            system.run_discovery_cycle(num_theorems=5, search_budget=10, max_candidates=1)
            stats = system.get_statistics()
            system.shutdown()
        except Exception as e:
            print(f"Warning: Could not run system for stats: {e}")
            stats = {}
            
    except Exception as e:
        print(f"Warning: Could not collect system statistics: {e}")
        stats = {}

    # 4. Generate Report
    reporter = MarkdownReporter(os.path.join(os.path.dirname(__file__), 'reports'))
    report_path = reporter.generate_report(final_results, stats)

    print(f"\nAudit Complete. Report generated at: {report_path}")
    print("="*80)

if __name__ == "__main__":
    run_audit()
