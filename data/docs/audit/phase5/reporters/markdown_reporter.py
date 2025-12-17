# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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

class MarkdownReporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, test_results, system_stats):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_report_phase5_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        passed_tests = [r for r in test_results if r.status == 'PASS']
        failed_tests = [r for r in test_results if r.status == 'FAIL']
        error_tests = [r for r in test_results if r.status == 'ERROR']
        
        total = len(test_results)
        success_rate = (len(passed_tests) / total * 100) if total > 0 else 0

        # Determine system status
        system_status = "Adaptive Cognitive Engine" if success_rate == 100 else "Optimization Incomplete"
        status_icon = "✅" if success_rate == 100 else "⚠️"

        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Phase 5 Audit Report: Production Optimization & Distillation\n\n")
            f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**System Status:** {system_status}\n\n")

            # Executive Summary
            f.write("## 1. Executive Summary\n\n")
            f.write(f"- **Total Tests:** {total}\n")
            f.write(f"- **Passed:** {len(passed_tests)} (✅)\n")
            f.write(f"- **Failed:** {len(failed_tests)} (❌)\n")
            f.write(f"- **Errors:** {len(error_tests)} (⚠️)\n")
            f.write(f"- **Success Rate:** {success_rate:.1f}%\n\n")

            if failed_tests or error_tests:
                f.write("> [!WARNING]\n")
                f.write("> Phase 5 audit identified issues. Please review the detailed results below.\n\n")
            else:
                f.write("> [!SUCCESS]\n")
                f.write("> Phase 5 Production Optimization is fully operational. The system has successfully transitioned to 'Adaptive Cognitive Engine' status (The Apex System).\n\n")

            # System Configuration
            f.write("## 2. System Configuration\n\n")
            f.write("### Apex System Architecture\n")
            f.write("- **Distillation & Harvest Team:** 2 Agents (Harvester, Trainer)\n")
            f.write("- **Hybrid Deployment Team:** 2 Agents (Gatekeeper, Fallback)\n")
            f.write("- **Operational Hardening Team:** 2 Agents (Simulator, IAM)\n")
            f.write("- **Evolutionary Flywheel:** Active Learning Loop Enabled\n\n")

            # Detailed Test Results
            f.write("## 3. Detailed Test Results\n\n")
            
            f.write("### Smoke Tests (Health & Initialization)\n")
            f.write("| Test Case | Status | Duration | Message |\n")
            f.write("| --- | --- | --- | --- |\n")
            smoke_tests = [r for r in test_results if 'smoke' in r.test_case.lower() or 'initialization' in r.test_case.lower() or 'presence' in r.test_case.lower() or 'health' in r.test_case.lower() or 'statistics' in r.test_case.lower()]
            for result in smoke_tests:
                status_icon = "✅ PASS" if result.status == 'PASS' else "❌ FAIL" if result.status == 'FAIL' else "⚠️ ERROR"
                f.write(f"| `{result.test_case}` | {status_icon} | {result.duration:.3f}s | {result.message} |\n")
            f.write("\n")

            f.write("### Edge Tests (Capabilities & Boundaries)\n")
            f.write("| Test Case | Status | Duration | Message |\n")
            f.write("| --- | --- | --- | --- |\n")
            edge_tests = [r for r in test_results if r not in smoke_tests]
            for result in edge_tests:
                status_icon = "✅ PASS" if result.status == 'PASS' else "❌ FAIL" if result.status == 'FAIL' else "⚠️ ERROR"
                f.write(f"| `{result.test_case}` | {status_icon} | {result.duration:.3f}s | {result.message} |\n")
            f.write("\n")

            # Production Statistics
            f.write("## 4. Production Statistics\n\n")
            
            if system_stats:
                # Hybrid Deployment
                gatekeeper = system_stats.get('complexity_gatekeeper', {})
                fallback = system_stats.get('confidence_fallback', {})
                
                f.write("### Hybrid Deployment (The Switch)\n")
                f.write(f"- **Total Queries:** {gatekeeper.get('total_queries', 0)}\n")
                f.write(f"- **Student Routed:** {gatekeeper.get('student_percentage', 0):.1f}%\n")
                f.write(f"- **Teacher Routed:** {gatekeeper.get('teacher_percentage', 0):.1f}%\n")
                f.write(f"- **Escalation Rate:** {fallback.get('escalation_rate', 0):.1f}%\n\n")

                # Distillation
                harvester = system_stats.get('thought_trace_harvester', {})
                f.write("### Knowledge Distillation\n")
                f.write(f"- **Corpus Size:** {harvester.get('corpus_size', 0)} verified traces\n")
                f.write(f"- **Verification Rate:** {harvester.get('verification_rate', 0):.1f}%\n")
                f.write(f"- **Escalated Traces:** {harvester.get('escalated_count', 0)}\n\n")

                # Evolution
                flywheel = system_stats.get('evolutionary_flywheel', {})
                f.write("### Evolutionary Flywheel\n")
                f.write(f"- **Evolution Cycles:** {flywheel.get('evolution_cycles', 0)}\n")
                f.write(f"- **Total Improvement:** {flywheel.get('total_improvement', 0):.1f}%\n")
                f.write(f"- **Current Phase:** {flywheel.get('current_phase', 'unknown')}\n\n")

        return filepath
