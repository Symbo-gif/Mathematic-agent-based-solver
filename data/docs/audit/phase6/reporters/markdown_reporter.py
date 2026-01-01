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

class MarkdownReporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, test_results, system_stats):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_report_phase6_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        passed_tests = [r for r in test_results if r.status == 'PASS']
        failed_tests = [r for r in test_results if r.status == 'FAIL']
        error_tests = [r for r in test_results if r.status == 'ERROR']
        
        total = len(test_results)
        success_rate = (len(passed_tests) / total * 100) if total > 0 else 0

        # Determine system status
        system_status = "Mathematical Discovery Engine" if success_rate == 100 else "Discovery Capabilities Incomplete"
        status_icon = "✅" if success_rate == 100 else "⚠️"

        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Phase 6 Audit Report: The Mathematical Discovery Engine\n\n")
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
                f.write("> Phase 6 audit identified issues. Please review the detailed results below.\n\n")
            else:
                f.write("> [!SUCCESS]\n")
                f.write("> Phase 6 is fully operational. The system has successfully transitioned to 'Mathematical Discovery Engine' status (The Researcher).\n\n")

            # System Configuration
            f.write("## 2. System Configuration\n\n")
            f.write("### Discovery Engine Architecture (13 Agents)\n")
            f.write("- **Conjecture Generation Team:** 3 Agents (Dreamer, Filter, Formalizer)\n")
            f.write("- **Deep Search Team:** 3 Agents (Tactician, Evaluator, Manager)\n")
            f.write("- **Algorithm Discovery Unit:** 3 Agents (Proposer, Evaluator, Distiller)\n")
            f.write("- **Undecidability Navigator:** 2 Agents (Checker, Liaison)\n")
            f.write("- **Formal Knowledge Integration:** 2 Agents (Pipeline, Updater)\n\n")

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

            # Discovery Statistics
            f.write("## 4. Discovery Statistics\n\n")
            
            if system_stats:
                sys_stats = system_stats.get('system', {})
                
                f.write("### Discovery Metrics\n")
                f.write(f"- **Discovery Cycles:** {sys_stats.get('discovery_cycles', 0)}\n")
                f.write(f"- **Theorems Generated:** {sys_stats.get('total_theorems_generated', 0)}\n")
                f.write(f"- **Proofs Found:** {sys_stats.get('total_proofs_found', 0)}\n")
                f.write(f"- **Algorithms Discovered:** {sys_stats.get('algorithms_discovered', 0)}\n")
                f.write(f"- **Discoveries Integrated:** {sys_stats.get('discoveries_integrated', 0)}\n\n")

                f.write("### Safety & Boundaries\n")
                f.write(f"- **Undecidable Problems Detected:** {sys_stats.get('undecidable_detected', 0)}\n")
                f.write(f"- **Human Guidance Requested:** {sys_stats.get('human_guidance_requested', 0)}\n\n")
                
                # Component specific stats
                gen_stats = system_stats.get('synthetic_data_generator', {})
                f.write("### Synthetic Data Generator\n")
                f.write(f"- **Total Generated:** {gen_stats.get('total_generated', 0)}\n")
                f.write(f"- **Unique Theorems:** {gen_stats.get('unique_theorems', 0)}\n")
                f.write(f"- **Algebra:** {gen_stats.get('algebra', 0)}\n")
                f.write(f"- **Geometry:** {gen_stats.get('geometry', 0)}\n")
                f.write(f"- **Number Theory:** {gen_stats.get('number_theory', 0)}\n\n")

                dec_stats = system_stats.get('decidability_checker', {})
                f.write("### Decidability Checker\n")
                f.write(f"- **Assessments:** {dec_stats.get('assessments', 0)}\n")
                f.write(f"- **Decidable Rate:** {dec_stats.get('decidable_rate_percent', 0)}%\n")
                f.write(f"- **Undecidable Rate:** {dec_stats.get('undecidable_rate_percent', 0)}%\n")

        return filepath
