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
        filename = f"audit_report_phase3_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Phase 3 Audit Report: Meta-Cognitive Middleware\n\n")
            f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**System Status:** Resilient Professional\n\n")

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
                f.write("> Phase 3 Meta-Cognitive Middleware is fully operational. The system has successfully transitioned from 'Fragile Genius' to 'Resilient Professional'.\n\n")
            else:
                f.write("> [!WARNING]\n")
                f.write("> Phase 3 audit identified issues. Please review the detailed results below.\n\n")

            # System Configuration
            f.write("## 2. System Configuration\n\n")
            f.write("### Meta-Cognitive Teams\n")
            f.write("- **Precondition Validation Team:** 4 Agents (Domain Checker, Assumption Validator, Edge Case Detector, Constraint Propagator)\n")
            f.write("- **Knowledge Management Team:** 3 Agents (Context Extractor, Memory Indexer, Retrieval Specialist)\n")
            f.write("- **Hypothesis Generation Team:** 3 Agents (Hypothesis Generator, Path Evaluator, Backtracking Manager)\n")
            f.write("- **Orchestrator:** Phase 3 Protocols (Pre-Flight, Look-Before-Leap, Scouting)\n\n")

            # Detailed Test Results
            f.write("## 3. Detailed Test Results\n\n")
            
            f.write("### Smoke Tests (Health & Initialization)\n")
            self._write_test_table(f, run_stats['results'], 'smoke')

            f.write("### Edge Tests (Capabilities & Boundaries)\n")
            self._write_test_table(f, run_stats['results'], 'edge')

            # System Statistics
            f.write("## 4. Meta-Cognitive Middleware Statistics\n\n")
            
            if 'orchestrator' in system_stats:
                orch_stats = system_stats['orchestrator']
                f.write("### Orchestrator\n")
                f.write(f"- Tasks Processed: {orch_stats.get('tasks_processed', 0)}\n")
                f.write(f"- Tasks Validated: {orch_stats.get('tasks_validated', 0)}\n")
                f.write(f"- Tasks Retrieved: {orch_stats.get('tasks_retrieved', 0)}\n")
                f.write(f"- Tasks Scouted: {orch_stats.get('tasks_scouted', 0)}\n\n")

                if 'precondition_team' in orch_stats:
                    pv_stats = orch_stats['precondition_team']
                    f.write("### Precondition Validation Team\n")
                    f.write(f"- Validations Performed: {pv_stats.get('validations_performed', 0)}\n")
                    f.write(f"- Rejections: {pv_stats.get('rejections', 0)}\n")
                    f.write(f"- Approval Rate: {pv_stats.get('approval_rate', 0):.1f}%\n\n")

                if 'knowledge_team' in orch_stats:
                    km_stats = orch_stats['knowledge_team']
                    f.write("### Knowledge Management Team\n")
                    f.write(f"- Context Extractions: {km_stats.get('context_extractor', {}).get('extractions_performed', 0)}\n")
                    f.write(f"- Results Indexed: {km_stats.get('memory_indexer', {}).get('entries_indexed', 0)}\n")
                    f.write(f"- Retrieval Queries: {km_stats.get('retrieval_specialist', {}).get('queries_performed', 0)}\n\n")

                if 'hypothesis_team' in orch_stats:
                    hg_stats = orch_stats['hypothesis_team']
                    f.write("### Hypothesis Generation Team\n")
                    f.write(f"- Hypotheses Generated: {hg_stats.get('hypothesis_generator', {}).get('hypotheses_generated', 0)}\n")
                    f.write(f"- Plans Evaluated: {hg_stats.get('path_evaluator', {}).get('evaluations_performed', 0)}\n")
                    f.write(f"- Backtracking Restorations: {hg_stats.get('backtracking_manager', {}).get('restorations_performed', 0)}\n\n")

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
