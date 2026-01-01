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
import datetime
import uuid
from typing import Dict, Any, List

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reporters.markdown_reporter import MarkdownReporter

class AuditTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.results_data = []
        self._start_time = None

    def startTest(self, test):
        self._start_time = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        duration = time.time() - self._start_time if self._start_time else 0.0
        super().addSuccess(test)
        self.results_data.append({
            'name': str(test),
            'status': 'PASS',
            'message': '',
            'duration': duration
        })

    def addFailure(self, test, err):
        duration = time.time() - self._start_time if self._start_time else 0.0
        super().addFailure(test, err)
        self.results_data.append({
            'name': str(test),
            'status': 'FAIL',
            'message': str(err[1]),
            'duration': duration
        })

    def addError(self, test, err):
        duration = time.time() - self._start_time if self._start_time else 0.0
        super().addError(test, err)
        self.results_data.append({
            'name': str(test),
            'status': 'ERROR',
            'message': str(err[1]),
            'duration': duration
        })

class AuditTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return AuditTestResult(self.stream, self.descriptions, self.verbosity)

def run_audit():
    print("=" * 80)
    print("PHASE 2 AUDIT SYSTEM - VERTICAL DOMAIN EXPANSION")
    print("=" * 80)
    print()

    start_time = time.time()
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='*_tests.py')
    
    print(f"Running tests from: {start_dir}")
    print(f"Run ID: {run_id}")
    print()

    # Run tests
    runner = AuditTestRunner(verbosity=2)
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time

    # Collect results
    results_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'summary': {
            'total': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors),
            'failed': len(result.failures),
            'errors': len(result.errors),
            'duration': duration
        },
        'tests': result.result.results_data if hasattr(result, 'result') else []
    }
    
    if hasattr(result, 'results_data'):
        results_data['tests'] = result.results_data

    # Generate Report
    print()
    print("Generating report...")
    reporter = MarkdownReporter(os.path.join(os.path.dirname(__file__), 'reports'))
    report_path = reporter.generate_report(run_id, results_data)
    
    print(f"Report generated: {report_path}")
    print()
    
    if result.wasSuccessful():
        print("[SUCCESS] Phase 2 Audit Passed")
        sys.exit(0)
    else:
        print("[FAILURE] Phase 2 Audit Failed")
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
