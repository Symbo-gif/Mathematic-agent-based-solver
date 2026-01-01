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

import os
import datetime
from typing import Dict, List, Any

class MarkdownReporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_report(self, run_id: str, results: Dict[str, Any]):
        """
        Generate a Markdown report for the audit run.
        """
        filename = f"audit_report_phase2_{run_id}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        timestamp = results.get('timestamp', datetime.datetime.now().isoformat())
        summary = results.get('summary', {})
        tests = results.get('tests', [])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Phase 2 Audit Report: Vertical Domain Expansion\n\n")
            f.write(f"**Run ID**: `{run_id}`\n")
            f.write(f"**Date**: {timestamp}\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write("| Metric | Value |\n")
            f.write("|---|---|\n")
            f.write(f"| Total Tests | {summary.get('total', 0)} |\n")
            f.write(f"| Passed | {summary.get('passed', 0)} |\n")
            f.write(f"| Failed | {summary.get('failed', 0)} |\n")
            f.write(f"| Errors | {summary.get('errors', 0)} |\n")
            
            success_rate = 0
            if summary.get('total', 0) > 0:
                success_rate = (summary.get('passed', 0) / summary.get('total', 1)) * 100
            
            f.write(f"| Success Rate | {success_rate:.1f}% |\n\n")
            
            status_icon = "✅" if summary.get('failed', 0) == 0 and summary.get('errors', 0) == 0 else "❌"
            f.write(f"**Overall Status**: {status_icon} {'PASSED' if status_icon == '✅' else 'FAILED'}\n\n")
            
            f.write("## Detailed Test Results\n\n")
            f.write("| Test Name | Status | Duration (s) | Message |\n")
            f.write("|---|---|---|---|\n")
            
            for test in tests:
                icon = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "⚠️"
                message = test.get('message', '').replace('\n', '<br>')
                f.write(f"| {test['name']} | {icon} {test['status']} | {test.get('duration', 0):.3f} | {message} |\n")
            
            f.write("\n## System Configuration\n\n")
            f.write("- **Phase**: 2 (Vertical Domain Expansion)\n")
            f.write("- **Status**: Fragile Genius\n")
            f.write("- **Components Tested**:\n")
            f.write("  - **Tier 2 Supervisors**: Algebra, Calculus, Linear Algebra, Statistics\n")
            f.write("  - **Tier 3 Specialists**:\n")
            f.write("    - Algebra: Arithmetic, Polynomial (Gröbner), Number Theory\n")
            f.write("    - Calculus: Differentiation, Integration (Dual-Engine), ODE, Series\n")
            f.write("    - Linear Algebra: Matrix Ops, Decomposition, Vector Space\n")
            f.write("    - Statistics: Distribution, Bayesian, Frequentist\n")
            f.write("    - Discrete: Combinatorics, Graph Theory\n")
            f.write("    - Numerical Fallback\n")
            
        return filepath
