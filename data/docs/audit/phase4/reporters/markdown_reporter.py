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

import datetime
import os
from typing import Dict, Any, List

class MarkdownReporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, run_stats: Dict[str, Any], system_stats: Dict[str, Any]) -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_report_phase4_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Phase 4 Audit Report: Dynamic Governance & Resilience\n\n")
            f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**System Status:** Self-Correcting System\n\n")

            # Executive Summary
            f.write("## 1. Executive Summary\n\n")
            f.write(f"- **Total Tests:** {run_stats['total']}\n")
            f.write(f"- **Passed:** {run_stats['passed']} (✅)\n")
            f.write(f"- **Failed:** {run_stats['failed']} (❌)\n")
            f.write(f"- **Errors:** {run_stats['errors']} (⚠️)\n")
            success_rate = (run_stats['passed'] / run_stats['total']) * 100 if run_stats['total'] > 0 else 0
            f.write(f"- **Success Rate:** {success_rate:.1f}%\n\n")

            if run_stats['failed'] == 0 and run_stats['errors'] == 0:
                f.write("> [!SUCCESS]\n")
                f.write("> Phase 4 Dynamic Governance is fully operational. The system has successfully transitioned from 'Resilient Professional' to 'Self-Correcting System'.\n\n")
            else:
                f.write("> [!WARNING]\n")
                f.write("> Phase 4 audit identified issues. Please review the detailed results below.\n\n")

            # System Configuration
            f.write("## 2. System Configuration\n\n")
            f.write("### Dynamic Governance Teams\n")
            f.write("- **Conflict Resolution Team:** 3 Agents (Debate Moderator, Evidence Weigher, Consensus Builder)\n")
            f.write("- **Failure Analysis Team:** 3 Agents (Error Classifier, Root Cause Analyzer, Alternative Path Generator)\n")
            f.write("- **Meta-Learning Team:** 3 Agents (Performance Monitor, Agent Selector Optimizer, Adaptive Dispatcher)\n")
            f.write("- **Protocols:** Appellate Protocol, Post-Mortem Protocol\n\n")

            # Detailed Test Results
            f.write("## 3. Detailed Test Results\n\n")
            
            f.write("### Smoke Tests (Health & Initialization)\n")
            self._write_test_table(f, run_stats['results'], 'smoke')

            f.write("### Edge Tests (Capabilities & Boundaries)\n")
            self._write_test_table(f, run_stats['results'], 'edge')

            # System Statistics
            f.write("## 4. Dynamic Governance Statistics\n\n")
            
            if 'conflict_resolution' in system_stats:
                crt_stats = system_stats['conflict_resolution']
                f.write("### Conflict Resolution Team\n")
                f.write(f"- Conflicts Resolved: {crt_stats.get('conflicts_resolved', 0)}\n")
                f.write(f"- Debates Moderated: {crt_stats.get('debate_moderator', {}).get('conflicts_detected', 0)}\n")
                f.write(f"- Cases Evaluated: {crt_stats.get('evidence_weigher', {}).get('cases_evaluated', 0)}\n")
                f.write(f"- Automatic Rulings: {crt_stats.get('evidence_weigher', {}).get('automatic_rulings', 0)}\n\n")

            if 'failure_analysis' in system_stats:
                fat_stats = system_stats['failure_analysis']
                f.write("### Failure Analysis Team\n")
                f.write(f"- Failures Handled: {fat_stats.get('failures_handled', 0)}\n")
                f.write(f"- Computational Errors: {fat_stats.get('error_classifier', {}).get('computational_errors', 0)}\n")
                f.write(f"- Logical Errors: {fat_stats.get('error_classifier', {}).get('logical_errors', 0)}\n")
                f.write(f"- Domain Errors: {fat_stats.get('error_classifier', {}).get('domain_errors', 0)}\n")
                f.write(f"- Alternatives Generated: {fat_stats.get('alternative_path_generator', {}).get('alternatives_generated', 0)}\n\n")

            if 'meta_learning' in system_stats:
                mlt_stats = system_stats['meta_learning']
                f.write("### Meta-Learning Team\n")
                f.write(f"- Optimization Runs: {mlt_stats.get('optimization_runs', 0)}\n")
                f.write(f"- Traces Recorded: {mlt_stats.get('performance_monitor', {}).get('traces_recorded', 0)}\n")
                f.write(f"- Patterns Discovered: {mlt_stats.get('optimizer', {}).get('patterns_discovered', 0)}\n\n")

        return filepath

    def _write_test_table(self, f, results: List[Dict], category_filter: str):
        f.write("| Test Case | Status | Duration | Message |\n")
        f.write("| --- | --- | --- | --- |\n")
        
        filtered_results = [r for r in results if category_filter in r['file']]
        
        if not filtered_results:
            f.write("| *No tests found* | - | - | - |\n\n")
            return

        for result in filtered_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            message = result['message'] if result['message'] else ""
            # Escape pipes in message
            message = message.replace("|", "\\|")
            f.write(f"| `{result['test_name']}` | {status_icon} {result['status']} | {result['duration']:.3f}s | {message} |\n")
        f.write("\n")
