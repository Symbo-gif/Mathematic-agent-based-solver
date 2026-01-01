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

"""
Report generation for stress test results.

Generates:
- Streaming progress logs (real-time updates)
- HTML interactive dashboards
- JSON machine-readable metrics
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading


class StreamingProgressLog:
    """
    Real-time progress log that streams to file.

    Useful for monitoring 30+ minute tests.
    """

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.start_time = datetime.now()
        self._lock = threading.Lock()

        # Initialize log file
        with open(self.log_path, 'w') as f:
            f.write(f"[{self._timestamp()}] Learning Systems Stress Test Started\n")
            f.write("="*80 + "\n\n")

    def _timestamp(self) -> str:
        """Get formatted timestamp"""
        elapsed = datetime.now() - self.start_time
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def log(self, message: str):
        """Write a timestamped message to log"""
        with self._lock:
            with open(self.log_path, 'a') as f:
                f.write(f"[{self._timestamp()}] {message}\n")

    def log_test_start(self, system_name: str, test_name: str):
        """Log test start"""
        self.log(f"{system_name} - {test_name} - STARTED")

    def log_test_complete(self, system_name: str, test_name: str, passed: bool, duration: float):
        """Log test completion"""
        status = "PASSED" if passed else "FAILED"
        self.log(f"{system_name} - {test_name} - {status} ({duration:.1f}s)")

    def log_progress(self, system_name: str, iteration: int, total: int, metric: Optional[str] = None):
        """Log iteration progress"""
        pct = (iteration / total * 100) if total > 0 else 0
        msg = f"{system_name} - Iteration {iteration}/{total} ({pct:.1f}%)"
        if metric:
            msg += f" - {metric}"
        self.log(msg)

    def log_checkpoint(self, tests_completed: int, tests_total: int, failures: int):
        """Log a checkpoint"""
        self.log(f"CHECKPOINT: {tests_completed}/{tests_total} tests complete, {failures} failures")

    def log_error(self, system_name: str, error: str):
        """Log an error"""
        self.log(f"ERROR [{system_name}]: {error}")

    def log_warning(self, system_name: str, warning: str):
        """Log a warning"""
        self.log(f"WARNING [{system_name}]: {warning}")


class HTMLReportGenerator:
    """
    Generates interactive HTML dashboard with charts.

    Shows:
    - Executive summary
    - Learning effectiveness metrics
    - Resource usage timelines (interactive charts)
    - Learning curves per system
    - Detailed test results
    """

    def generate(self, results: Dict[str, Any], output_path: Path):
        """
        Generate HTML report.

        Args:
            results: Dictionary with all test results
            output_path: Path to output HTML file
        """
        html = self._build_html(results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"[HTMLReportGenerator] Report generated: {output_path}")

    def _build_html(self, results: Dict[str, Any]) -> str:
        """Build the complete HTML document"""
        # Extract summary stats
        summary = results.get('summary', {})
        systems = results.get('systems', {})
        resource_summary = results.get('resource_summary', {})

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Systems Stress Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .metric-card.success {{
            border-left-color: #27ae60;
        }}
        .metric-card.warning {{
            border-left-color: #f39c12;
        }}
        .metric-card.error {{
            border-left-color: #e74c3c;
        }}
        .metric-label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .verdict {{
            font-size: 24px;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            text-align: center;
        }}
        .verdict.excellent {{
            background: #d4edda;
            color: #155724;
            border: 2px solid #27ae60;
        }}
        .verdict.good {{
            background: #fff3cd;
            color: #856404;
            border: 2px solid #f39c12;
        }}
        .verdict.fair {{
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #e74c3c;
        }}
        .expandable {{
            cursor: pointer;
            user-select: none;
        }}
        .expandable:hover {{
            background: #e8f4f8;
        }}
        .details {{
            display: none;
            padding: 15px;
            background: #f8f9fa;
            border-left: 3px solid #3498db;
            margin: 10px 0;
        }}
        .details.show {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Learning Systems Extreme Stress Test Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duration:</strong> {summary.get('total_duration_minutes', 0):.1f} minutes</p>

        <!-- Verdict -->
        {self._render_verdict(summary)}

        <!-- Summary Metrics -->
        <h2>Executive Summary</h2>
        <div class="summary-grid">
            {self._render_metric_card('Tests Passed', f"{summary.get('tests_passed', 0)}/{summary.get('tests_total', 0)}",
                'success' if summary.get('pass_rate', 0) >= 0.9 else 'warning')}
            {self._render_metric_card('Pass Rate', f"{summary.get('pass_rate', 0)*100:.1f}%",
                'success' if summary.get('pass_rate', 0) >= 0.9 else 'warning')}
            {self._render_metric_card('Avg Improvement', f"{summary.get('avg_improvement_percent', 0):+.1f}%",
                'success' if summary.get('avg_improvement_percent', 0) >= 10 else 'warning')}
            {self._render_metric_card('Memory Leaks', 'None' if not resource_summary.get('memory_leak_detected') else 'DETECTED',
                'success' if not resource_summary.get('memory_leak_detected') else 'error')}
            {self._render_metric_card('Thread Explosions', 'None' if not resource_summary.get('thread_explosion_detected') else 'DETECTED',
                'success' if not resource_summary.get('thread_explosion_detected') else 'error')}
            {self._render_metric_card('Peak Memory', f"{resource_summary.get('peak_memory_mb', 0):.0f} MB",
                'success' if resource_summary.get('peak_memory_mb', 0) < 2000 else 'warning')}
        </div>

        <!-- System Results Table -->
        <h2>System-by-System Results</h2>
        <table>
            <thead>
                <tr>
                    <th>System</th>
                    <th>Tests Passed</th>
                    <th>Improvement</th>
                    <th>Effectiveness</th>
                    <th>Convergence</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {self._render_system_rows(systems)}
            </tbody>
        </table>

        <!-- Resource Usage Summary -->
        <h2>Resource Usage</h2>
        <table>
            <tr>
                <td>Peak Memory</td>
                <td>{resource_summary.get('peak_memory_mb', 0):.2f} MB</td>
            </tr>
            <tr>
                <td>Average Memory</td>
                <td>{resource_summary.get('avg_memory_mb', 0):.2f} MB</td>
            </tr>
            <tr>
                <td>Peak CPU</td>
                <td>{resource_summary.get('peak_cpu_percent', 0):.1f}%</td>
            </tr>
            <tr>
                <td>Peak Threads</td>
                <td>{resource_summary.get('peak_threads', 0)}</td>
            </tr>
            <tr>
                <td>Memory Leak Detected</td>
                <td class="{'fail' if resource_summary.get('memory_leak_detected') else 'pass'}">
                    {'YES' if resource_summary.get('memory_leak_detected') else 'NO'}
                </td>
            </tr>
        </table>

        <!-- Detailed Results (Expandable) -->
        <h2>Detailed Test Results</h2>
        {self._render_detailed_results(systems)}

    </div>

    <script>
        function toggleDetails(id) {{
            const details = document.getElementById(id);
            details.classList.toggle('show');
        }}
    </script>
</body>
</html>"""
        return html

    def _render_verdict(self, summary: Dict) -> str:
        """Render the verdict banner"""
        pass_rate = summary.get('pass_rate', 0)
        improvement = summary.get('avg_improvement_percent', 0)
        no_leaks = not summary.get('memory_leak_detected', False)

        if pass_rate >= 0.9 and improvement >= 10 and no_leaks:
            verdict_class = 'excellent'
            verdict_text = 'EXCELLENT - All learning systems are production-ready!'
        elif pass_rate >= 0.75 and improvement >= 5:
            verdict_class = 'good'
            verdict_text = 'GOOD - Most systems are stable, minor issues detected'
        else:
            verdict_class = 'fair'
            verdict_text = 'FAIR - Significant issues detected, review required'

        return f'<div class="verdict {verdict_class}">{verdict_text}</div>'

    def _render_metric_card(self, label: str, value: str, card_class: str = '') -> str:
        """Render a metric card"""
        return f"""
        <div class="metric-card {card_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>"""

    def _render_system_rows(self, systems: Dict) -> str:
        """Render system result table rows"""
        rows = []
        for system_name, system_data in systems.items():
            tests_passed = system_data.get('tests_passed', 0)
            tests_total = system_data.get('tests_total', 0)
            improvement = system_data.get('avg_improvement_percent', 0)
            effectiveness = system_data.get('avg_effectiveness', 0)
            convergence = system_data.get('convergence_rate', 0)
            status = 'PASS' if tests_passed == tests_total else 'FAIL'
            status_class = 'pass' if status == 'PASS' else 'fail'

            rows.append(f"""
            <tr>
                <td><strong>{system_name}</strong></td>
                <td>{tests_passed}/{tests_total}</td>
                <td>{improvement:+.1f}%</td>
                <td>{effectiveness:.2f}</td>
                <td>{convergence*100:.0f}%</td>
                <td class="{status_class}">{status}</td>
            </tr>""")

        return '\n'.join(rows)

    def _render_detailed_results(self, systems: Dict) -> str:
        """Render expandable detailed results"""
        details = []
        for system_name, system_data in systems.items():
            tests = system_data.get('tests', [])
            details_id = f"details_{system_name.replace(' ', '_')}"

            test_list = '<ul>'
            for test in tests:
                test_name = test.get('name', 'Unknown')
                passed = test.get('passed', False)
                improvement = test.get('improvement_percent', 0)
                status_class = 'pass' if passed else 'fail'
                test_list += f'<li class="{status_class}">{test_name}: {improvement:+.1f}% improvement</li>'
            test_list += '</ul>'

            details.append(f"""
            <div class="expandable" onclick="toggleDetails('{details_id}')">
                [+] {system_name}
            </div>
            <div id="{details_id}" class="details">
                {test_list}
            </div>""")

        return '\n'.join(details)


class JSONMetricsExporter:
    """
    Exports machine-readable JSON metrics.
    """

    def export(self, results: Dict[str, Any], output_path: Path):
        """
        Export results to JSON.

        Args:
            results: Complete results dictionary
            output_path: Path to output JSON file
        """
        # Add metadata
        results['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'report_version': '1.0'
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"[JSONMetricsExporter] Metrics exported: {output_path}")
